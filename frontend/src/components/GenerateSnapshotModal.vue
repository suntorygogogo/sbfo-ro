<template>
  <el-dialog
    v-model="visible"
    title="Lock IBP Step View"
    width="520px"
    :close-on-click-modal="false"
    @closed="onClosed"
  >
    <p class="modal-subtitle">
      Create a locked snapshot of database entries filtered by IBP Step for the selected period.
    </p>

    <el-form label-position="top" class="snapshot-form">
      <!-- Snapshot Period -->
      <el-form-item label="Snapshot Period">
        <div class="period-row">
          <el-select v-model="form.period" placeholder="Period" class="period-select">
            <el-option v-for="p in PERIODS" :key="p" :label="p" :value="p" />
          </el-select>
          <el-select v-model="form.year" placeholder="Year" class="year-select">
            <el-option v-for="y in yearOptions" :key="y" :label="y" :value="y" />
          </el-select>
        </div>
        <div v-if="entryCount !== null" class="entry-count-hint">
          <span v-if="form.ibpStep">This will snapshot {{ entryCount }} entries</span>
        </div>
      </el-form-item>

      <!-- IBP Step -->
      <el-form-item label="IBP Step" required>
        <el-select
          v-model="form.ibpStep"
          placeholder="Select IBP Step"
          class="full-width"
          :loading="ibpStepLoading"
          clearable
          @change="onIbpStepChange"
        >
          <el-option v-for="step in ibpStepOptions" :key="step" :label="step" :value="step" />
        </el-select>
        <div v-if="form.ibpStep && entryCount !== null" :class="['entry-count-hint', entryCount === 0 ? 'count-zero' : '']">
          <template v-if="entryCount === 0">
            No entries found for this IBP Step — snapshot cannot be created.
          </template>
          <template v-else>
            This will snapshot {{ entryCount }} entries
          </template>
        </div>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">Cancel</el-button>
      <el-button
        type="primary"
        :disabled="!form.ibpStep || entryCount === 0"
        :loading="creating"
        @click="handleCreate"
      >
        Create Snapshot
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, computed } from "vue";
import { ElMessage } from "element-plus";
import { snapshotApi, lookupApi } from "@/services/api";
import { PERIODS } from "@/types";
import type { AppUser } from "@/types";

const props = defineProps<{
  modelValue: boolean;
  currentUser: AppUser | null;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", val: boolean): void;
  (e: "created"): void;
}>();

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit("update:modelValue", v),
});

// Default period = current fiscal month, year = current year
const now = new Date();
const defaultPeriod = `F${String(now.getMonth() + 1).padStart(2, "0")}`;
const defaultYear = String(now.getFullYear());

const yearOptions = computed(() => {
  const y = now.getFullYear();
  return [String(y - 1), String(y), String(y + 1)];
});

const form = ref({
  period: defaultPeriod,
  year: defaultYear,
  ibpStep: "",
});

const ibpStepOptions = ref<string[]>([]);
const ibpStepLoading = ref(false);
const entryCount = ref<number | null>(null);
const countLoading = ref(false);
const creating = ref(false);

async function loadIbpSteps() {
  ibpStepLoading.value = true;
  try {
    ibpStepOptions.value = await lookupApi.get("ibp_step");
  } finally {
    ibpStepLoading.value = false;
  }
}

async function onIbpStepChange(val: string) {
  if (!val) {
    entryCount.value = null;
    return;
  }
  countLoading.value = true;
  try {
    const { count } = await snapshotApi.getCount(val);
    entryCount.value = count;
  } finally {
    countLoading.value = false;
  }
}

async function handleCreate() {
  if (!form.value.ibpStep) {
    ElMessage.warning("Please select an IBP Step");
    return;
  }
  if (!props.currentUser) {
    ElMessage.error("No current user");
    return;
  }
  creating.value = true;
  try {
    await snapshotApi.create({
      period: form.value.period,
      year: form.value.year,
      ibpStep: form.value.ibpStep,
      createdBy: props.currentUser.email,
    });
    ElMessage.success("Snapshot created successfully");
    visible.value = false;
    emit("created");
  } catch {
    ElMessage.error("Failed to create snapshot");
  } finally {
    creating.value = false;
  }
}

function onClosed() {
  form.value = { period: defaultPeriod, year: defaultYear, ibpStep: "" };
  entryCount.value = null;
}

watch(
  () => props.modelValue,
  (open) => {
    if (open && ibpStepOptions.value.length === 0) loadIbpSteps();
  }
);
</script>

<style scoped>
.modal-subtitle {
  color: var(--text-secondary);
  font-size: 14px;
  margin: 0 0 20px;
}

.snapshot-form {
  margin-top: 4px;
}

.period-row {
  display: flex;
  gap: 10px;
  width: 100%;
}

.period-select {
  flex: 1;
}

.year-select {
  width: 110px;
}

.full-width {
  width: 100%;
}

.entry-count-hint {
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 6px;
}

.count-zero {
  color: var(--el-color-danger);
}
</style>
