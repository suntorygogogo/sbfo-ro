<template>
  <div class="page-container">
    <!-- Header -->
    <div class="page-header">
      <el-button :icon="ArrowLeft" text class="back-btn" @click="router.push('/')">
        Back to Main
      </el-button>

      <div class="header-main">
        <div>
          <h1 class="page-title">View Snapshots</h1>
          <p class="page-subtitle">View and manage frozen snapshots of entry versions</p>
        </div>
        <el-button
          v-if="!compareMode"
          :icon="Sort"
          class="compare-btn"
          :disabled="groupedSnapshots.length === 0"
          @click="enterCompareMode"
        >
          Compare Snapshots
        </el-button>
      </div>
    </div>

    <!-- Compare mode banner -->
    <div v-if="compareMode" class="compare-banner">
      <div class="banner-left">
        <el-icon class="banner-icon"><InfoFilled /></el-icon>
        <span v-if="selected.length === 0">Select 2 snapshots to compare</span>
        <span v-else-if="selected.length === 1">1 snapshot selected — select 1 more</span>
        <span v-else>
          <strong>2 snapshots selected.</strong>
          First selected = Baseline &nbsp;·&nbsp; Second selected = Comparison
        </span>
      </div>
      <div class="banner-right">
        <el-button
          type="primary"
          :disabled="selected.length !== 2"
          @click="goCompare"
        >
          Compare
        </el-button>
        <el-button @click="exitCompareMode">Cancel</el-button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" v-loading="true" style="height: 200px;" />

    <!-- Empty -->
    <el-empty v-else-if="groupedSnapshots.length === 0" description="No snapshots yet" style="margin-top: 60px;" />

    <!-- Grouped by IBP Step -->
    <div v-else class="groups">
      <div v-for="group in groupedSnapshots" :key="group.ibpStep" class="group">
        <div class="group-header">
          <span class="group-title">{{ group.ibpStep }}</span>
          <el-tag size="small" round type="info" class="group-count">
            {{ group.snapshots.length }} snapshot{{ group.snapshots.length !== 1 ? 's' : '' }}
          </el-tag>
        </div>

        <div class="cards-grid">
          <div
            v-for="snap in group.snapshots"
            :key="snap.id"
            :class="['snapshot-card', compareMode && isSelected(snap.id) && 'card-selected']"
            @click="compareMode && toggleSelect(snap)"
          >
            <div class="card-body">
              <div class="card-title-row">
                <div class="card-title">{{ snap.ibpStep }} - {{ snap.period }} {{ snap.year }}</div>
                <div v-if="compareMode" class="card-checkbox">
                  <el-checkbox
                    :model-value="isSelected(snap.id)"
                    :disabled="!isSelected(snap.id) && selected.length >= 2"
                    @change="toggleSelect(snap)"
                    @click.stop
                  />
                  <el-tag
                    v-if="isSelected(snap.id)"
                    size="small"
                    :type="selectedIndex(snap.id) === 0 ? 'primary' : 'success'"
                    class="order-tag"
                  >
                    {{ selectedIndex(snap.id) === 0 ? 'Baseline' : 'Compare' }}
                  </el-tag>
                </div>
              </div>
              <div class="card-meta">Created: {{ formatDate(snap.createdAt) }}</div>
              <div class="card-count">{{ snap.entryCount }} {{ snap.entryCount === 1 ? 'entry' : 'entries' }} frozen</div>
            </div>
            <div v-if="!compareMode" class="card-footer">
              <el-button class="view-btn" @click="router.push(`/snapshots/${snap.id}`)">View Snapshot</el-button>
              <el-button
                class="delete-btn"
                :icon="Delete"
                :loading="deletingId === snap.id"
                @click="handleDelete(snap)"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ArrowLeft, Delete, Sort, InfoFilled } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { snapshotApi } from "@/services/api";
import type { Snapshot } from "@/types";

const router = useRouter();

const loading = ref(false);
const snapshots = ref<Snapshot[]>([]);
const deletingId = ref<number | null>(null);

// Compare mode
const compareMode = ref(false);
const selected = ref<Snapshot[]>([]);

function enterCompareMode() {
  compareMode.value = true;
  selected.value = [];
}

function exitCompareMode() {
  compareMode.value = false;
  selected.value = [];
}

function isSelected(id: number) {
  return selected.value.some((s) => s.id === id);
}

function selectedIndex(id: number) {
  return selected.value.findIndex((s) => s.id === id);
}

function toggleSelect(snap: Snapshot) {
  if (isSelected(snap.id)) {
    selected.value = selected.value.filter((s) => s.id !== snap.id);
  } else if (selected.value.length < 2) {
    selected.value = [...selected.value, snap];
  }
}

function goCompare() {
  if (selected.value.length !== 2) return;
  const [base, cmp] = selected.value;
  router.push(`/snapshots/compare?base=${base.id}&compare=${cmp.id}`);
}

const groupedSnapshots = computed(() => {
  const map = new Map<string, Snapshot[]>();
  for (const s of snapshots.value) {
    if (!map.has(s.ibpStep)) map.set(s.ibpStep, []);
    map.get(s.ibpStep)!.push(s);
  }
  return Array.from(map.entries()).map(([ibpStep, snaps]) => ({ ibpStep, snapshots: snaps }));
});

async function loadSnapshots() {
  loading.value = true;
  try {
    const { snapshots: list } = await snapshotApi.list();
    snapshots.value = list;
  } catch {
    ElMessage.error("Failed to load snapshots");
  } finally {
    loading.value = false;
  }
}

async function handleDelete(snapshot: Snapshot) {
  try {
    await ElMessageBox.confirm(
      `Delete snapshot "${snapshot.ibpStep} - ${snapshot.period} ${snapshot.year}"? This cannot be undone.`,
      "Delete Snapshot",
      { type: "warning", confirmButtonText: "Delete", confirmButtonClass: "el-button--danger" }
    );
    deletingId.value = snapshot.id;
    await snapshotApi.delete(snapshot.id);
    snapshots.value = snapshots.value.filter((s) => s.id !== snapshot.id);
    ElMessage.success("Snapshot deleted");
  } catch {
    // cancelled or error — no action needed
  } finally {
    deletingId.value = null;
  }
}

function formatDate(iso: string) {
  if (!iso) return "";
  return new Date(iso).toLocaleString("en-AU", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

onMounted(loadSnapshots);
</script>

<style scoped>
.page-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px 32px;
}

.page-header {
  margin-bottom: 36px;
}

.back-btn {
  margin-bottom: 16px;
  padding-left: 0;
  color: var(--text-secondary);
}

.header-main {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 6px;
  color: var(--text-primary);
  line-height: 1.2;
}

.page-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

.compare-btn {
  color: var(--text-secondary);
  border-color: var(--border-color);
}

/* Compare mode banner */
.compare-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  padding: 12px 20px;
  margin-bottom: 28px;
  flex-wrap: wrap;
}

.banner-left {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #1e40af;
}

.banner-icon {
  font-size: 18px;
  color: #3b82f6;
  flex-shrink: 0;
}

.banner-right {
  display: flex;
  gap: 8px;
}

/* Groups */
.groups {
  display: flex;
  flex-direction: column;
  gap: 36px;
}

.group-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.group-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}

.group-count {
  font-size: 12px;
}

/* Cards */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.snapshot-card {
  border: 1px solid var(--border-color);
  border-radius: 10px;
  overflow: hidden;
  background: var(--bg-primary);
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.snapshot-card.card-selected {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.25);
}

.compare-mode-active .snapshot-card:not(.card-selected) {
  opacity: 0.7;
}

.card-body {
  padding: 18px 18px 14px;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
  cursor: default;
}

.card-title-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.3;
}

.card-checkbox {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.order-tag {
  font-size: 11px;
}

.card-meta {
  font-size: 13px;
  color: var(--text-secondary);
}

.card-count {
  font-size: 13px;
  color: var(--text-muted);
  margin-top: 4px;
}

.card-footer {
  padding: 0 12px 12px;
  display: flex;
  gap: 8px;
}

.view-btn {
  flex: 1;
  background: #1a1a1a;
  color: #fff;
  border-color: #1a1a1a;
  border-radius: 6px;
  font-weight: 500;
}

.view-btn:hover {
  background: #333;
  border-color: #333;
  color: #fff;
}

.delete-btn {
  background: var(--el-color-danger);
  border-color: var(--el-color-danger);
  color: #fff;
  border-radius: 6px;
  width: 36px;
  padding: 0;
}

.delete-btn:hover {
  background: var(--el-color-danger-dark-2);
  border-color: var(--el-color-danger-dark-2);
  color: #fff;
}

@media (max-width: 1024px) {
  .cards-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .cards-grid {
    grid-template-columns: 1fr;
  }
}
</style>
