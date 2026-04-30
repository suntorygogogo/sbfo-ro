<template>
  <div class="page-container">
    <!-- Header -->
    <div class="main-header">
      <div class="header-left">
        <h1 class="page-title">Risk and Opportunities Tracker</h1>
        <p class="page-subtitle">
          Create and manage Risks and Opportunities across your business units
        </p>
      </div>
      <div class="header-right">
        <div class="role-switcher">
          <el-icon class="role-icon"><User /></el-icon>
          <div class="role-meta">
            <span class="role-label">Logged in as</span>
            <!-- LOCAL: manual user selector -->
            <el-select
              v-if="authMode === 'LOCAL'"
              v-model="store.currentUser"
              class="role-picker"
              size="default"
              value-key="id"
              placeholder="Select user email"
              clearable
            >
              <el-option
                v-for="u in store.users"
                :key="u.id"
                :value="u"
                :label="u.email"
              >
                <span>{{ u.email }}</span>
                <span class="user-role-tag">{{ ROLE_MAP[u.role] }}</span>
              </el-option>
            </el-select>
            <!-- DBX + System Admin: test-user impersonation dropdown -->
            <template v-else-if="authMode === 'DBX' && dbxAdminUser?.role === 0">
              <span class="role-email">{{ dbxAdminUser.email }}</span>
              <el-select
                v-model="store.currentUser"
                class="role-picker"
                size="default"
                value-key="id"
                placeholder="Test as..."
                clearable
                style="margin-left: 8px;"
                @clear="store.currentUser = dbxAdminUser"
              >
                <el-option
                  v-for="u in store.users.filter(u => !u.email.endsWith('@suntory.com'))"
                  :key="u.id"
                  :value="u"
                  :label="u.email"
                >
                  <span>{{ u.email }}</span>
                  <span class="user-role-tag">{{ ROLE_MAP[u.role] }}</span>
                </el-option>
              </el-select>
            </template>
            <!-- DBX: plain identity display -->
            <span v-else class="role-email">
              {{ store.currentUser?.email ?? "Resolving identity..." }}
            </span>
          </div>
        </div>

        <div class="snapshot-actions">
          <el-button
            v-if="store.userRole === 'System Admin'"
            :icon="Lock"
            @click="generateSnapshotOpen = true"
          >
            Generate Snapshot
          </el-button>
          <el-button text @click="router.push('/snapshots')">View Snapshots</el-button>
        </div>

        <el-button
          v-if="store.canCreate"
          type="primary"
          :icon="Plus"
          @click="openCreate"
        >
          Add Entry
        </el-button>
      </div>
    </div>

    <!-- Generate Snapshot Modal -->
    <GenerateSnapshotModal
      v-model="generateSnapshotOpen"
      :current-user="store.currentUser"
      @created="onSnapshotCreated"
    />

    <!-- Table -->
    <EntriesTable
      :entries="store.displayEntries"
      :can-approve="store.canApprove"
      export-filename="RO_Tracker"
      @edit="openEdit"
      @duplicate="openDuplicate"
      @delete="handleDelete"
      @history="goToHistory"
      @approve="handleApprove"
    />

    <!-- Entry Form Dialog -->
    <el-dialog
      v-model="formOpen"
      :title="editingEntry ? 'Edit Entry' : 'New Entry'"
      width="900px"
      :close-on-click-modal="false"
      @closed="editingEntry = null"
    >
      <EntryForm ref="formRef" :entry="editingEntry" />
      <template #footer>
        <el-button @click="formOpen = false">Cancel</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          {{ editingEntry ? "Save Changes" : "Create Entry" }}
        </el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { Plus, User, Lock } from "@element-plus/icons-vue";
import { useEntryStore } from "@/stores/entryStore";
import { authApi, entryApi } from "@/services/api";
import EntriesTable from "@/components/EntriesTable.vue";
import EntryForm from "@/components/EntryForm.vue";
import GenerateSnapshotModal from "@/components/GenerateSnapshotModal.vue";
import type { Entry } from "@/types";
import { ROLE_MAP } from "@/types";

const router = useRouter();
const store = useEntryStore();

const formOpen = ref(false);
const editingEntry = ref<Entry | null>(null);
const saving = ref(false);
const formRef = ref<InstanceType<typeof EntryForm> | null>(null);
const authMode = ref<"LOCAL" | "DBX">("LOCAL");
const dbxAdminUser = ref<import("@/types").AppUser | null>(null);
const generateSnapshotOpen = ref(false);

onMounted(async () => {
  try {
    const { auth_mode } = await authApi.getConfig();
    authMode.value = auth_mode;
  } catch {
    authMode.value = "LOCAL";
  }
  if (authMode.value === "DBX") {
    try {
      const me = await authApi.getMe();
      store.currentUser = me;
      // System Admin in DBX mode: load test users (non-@suntory.com) for impersonation
      if (me.role === 0) {
        dbxAdminUser.value = me;
        await store.fetchUsers();
      }
    } catch (e: unknown) {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      ElMessage.error(msg ?? "Your account is not registered. Please contact your administrator.");
    }
  } else {
    await store.fetchUsers();
  }
  store.fetchEntries();
});

watch(() => store.currentUser, () => { store.fetchEntries(); });

function openCreate() {
  editingEntry.value = null;
  formOpen.value = true;
}

function openEdit(entry: Entry) {
  editingEntry.value = { ...entry };
  formOpen.value = true;
}

function openDuplicate(entry: Entry) {
  editingEntry.value = null;
  formOpen.value = true;
  // Pre-fill form with copied data (minus id/version)
  setTimeout(() => {
    const hasChildren = entry.childImpacts && entry.childImpacts.length > 0;
    const copy = {
      ...entry,
      id: 0,
      version: 0,
      originalEntryId: undefined,
      status: "Open",
      ...(hasChildren ? { impactPeriod: undefined, impactYear: undefined, impactValue: undefined, secondaryValue: undefined } : {}),
    };
    editingEntry.value = copy;
  }, 10);
}

async function handleSave() {
  if (!formRef.value) return;
  const data = await formRef.value.validate();
  if (!data) return;

  saving.value = true;
  try {
    const payload = {
      creation_date: editingEntry.value?.creationDate ?? new Date().toISOString().slice(0, 10),
      creation_date_period: data.creationDatePeriod,
      creation_date_year: data.creationDateYear,
      add_to_forecast_by_period: data.addToForecastByPeriod,
      add_to_forecast_by_year: data.addToForecastByYear,
      division: data.division,
      ibp_step: data.ibpStep,
      country: data.country,
      channel: data.channel,
      sub_channel: data.subChannel,
      account: data.account,
      brand: data.brand,
      brand_family: data.brandFamily,
      r_and_o: data.rAndO,
      probability: data.probability,
      categorisation: data.categorisation,
      impact_period: data.impactPeriod,
      impact_year: data.impactYear,
      nsv_aud: data.nsvAud,
      nsv_nzd: data.nsvNzd,
      volume_litres: data.volumeLitres,
      impact_type: data.impactType,
      owner: data.owner,
      creator: data.creator,
      modified_user: store.currentUser?.email ?? null,
      status: data.status,
      description: data.description,
      child_impacts: data.childImpacts.map((ci) => ({
        impact_year: ci.impactYear,
        impact_period: ci.impactPeriod,
        nsv_aud: ci.nsvAud,
        nsv_nzd: ci.nsvNzd,
        volume_litres: ci.volumeLitres,
      })),
    };

    if (editingEntry.value && editingEntry.value.id) {
      await store.updateEntry(editingEntry.value.id, payload as unknown as Partial<Entry>);
      ElMessage.success("Entry updated");
    } else {
      await store.createEntry(payload as unknown as Partial<Entry>);
      ElMessage.success("Entry created");
    }
    formOpen.value = false;
  } catch {
    ElMessage.error("Failed to save entry");
  } finally {
    saving.value = false;
  }
}

async function handleDelete(entry: Entry) {
  try {
    await ElMessageBox.confirm(
      "This will delete all versions of this entry. Continue?",
      "Confirm Delete",
      { type: "warning", confirmButtonText: "Delete", confirmButtonClass: "el-button--danger" }
    );
    await store.deleteEntry(entry.id);
    ElMessage.success("Entry deleted");
  } catch {
    // cancelled
  }
}

async function handleApprove(entry: Entry) {
  try {
    const { status: latestStatus } = await entryApi.getStatus(entry.id);
    if (latestStatus !== entry.status) {
      ElMessage.warning(`This entry's status has changed to "${latestStatus}". Please review the latest state.`);
      await store.fetchEntries();
      return;
    }
    await store.approveEntry(entry.id, store.currentUser?.email);
    ElMessage.success("Entry approved");
  } catch {
    ElMessage.error("Unable to verify entry status. Please refresh and try again.");
    await store.fetchEntries();
  }
}

function goToHistory(entry: Entry) {
  router.push(`/entry/${entry.originalEntryId || entry.id}/history`);
}

function onSnapshotCreated() {
  // No-op for now; snapshot list is on a separate page
}
</script>

<style scoped>
.page-container {
  max-width: 1600px;
  margin: 0 auto;
  padding: 24px;
}

.main-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  gap: 16px;
  flex-wrap: wrap;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: calc(var(--radius) + 4px);
  box-shadow: var(--shadow-sm);
  padding: 20px;
}

.header-left {
  flex: 1;
  min-width: 320px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 6px;
  color: var(--text-primary);
  line-height: 1.2;
}

.page-subtitle {
  font-size: 15px;
  color: var(--text-secondary);
  margin: 0;
}

.header-right {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.snapshot-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.role-switcher {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  background: var(--bg-secondary);
}

.role-icon {
  color: var(--text-muted);
}

.role-meta {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.role-label {
  font-size: 11px;
  line-height: 1;
  color: var(--text-muted);
}

.role-picker {
  width: 220px;
}

.user-role-tag {
  float: right;
  font-size: 11px;
  color: var(--text-muted);
  margin-left: 8px;
}

.role-email {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  padding: 0 4px;
}

@media (max-width: 768px) {
  .main-header {
    align-items: flex-start;
    padding: 16px;
  }

  .page-title {
    font-size: 22px;
  }

  .header-right {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
