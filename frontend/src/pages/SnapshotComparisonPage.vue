<template>
  <div class="page-container">
    <!-- Header -->
    <div class="page-header">
      <el-button :icon="ArrowLeft" text class="back-btn" @click="router.push('/snapshots')">
        Back to Snapshots
      </el-button>

      <div class="header-main">
        <div>
          <h1 class="page-title">Snapshot Comparison</h1>
          <p class="page-subtitle" v-if="baseSnap && compareSnap">
            <span class="snap-label base-label">Baseline</span>
            {{ baseSnap.ibpStep }} — {{ baseSnap.period }} {{ baseSnap.year }}
            &nbsp;vs&nbsp;
            <span class="snap-label compare-label">Comparison</span>
            {{ compareSnap.ibpStep }} — {{ compareSnap.period }} {{ compareSnap.year }}
          </p>
        </div>

        <div class="summary-pills" v-if="!loading && diffResult">
          <el-tag type="danger" size="large" class="pill">
            <span class="pill-num">{{ diffResult.deleted.length }}</span> Deleted
          </el-tag>
          <el-tag type="success" size="large" class="pill">
            <span class="pill-num">{{ diffResult.added.length }}</span> New
          </el-tag>
          <el-tag type="warning" size="large" class="pill">
            <span class="pill-num">{{ diffResult.modified.length }}</span> Modified
          </el-tag>
          <el-tag type="info" size="large" class="pill">
            <span class="pill-num">{{ diffResult.unchanged.length }}</span> Unchanged
          </el-tag>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" v-loading="true" style="height: 300px;" />

    <!-- Error -->
    <el-empty v-else-if="error" :description="error" style="margin-top: 60px;" />

    <!-- Results -->
    <div v-else-if="diffResult" class="results">

      <!-- Tabs + Columns toolbar -->
      <div class="toolbar-row">
        <el-tabs v-model="activeTab" class="result-tabs">
          <el-tab-pane name="all" :label="`All (${allRows.length})`" />
          <el-tab-pane name="deleted" :label="`Deleted (${diffResult.deleted.length})`" />
          <el-tab-pane name="added" :label="`New (${diffResult.added.length})`" />
          <el-tab-pane name="modified" :label="`Modified (${diffResult.modified.length})`" />
          <el-tab-pane name="unchanged" :label="`Unchanged (${diffResult.unchanged.length})`" />
        </el-tabs>

        <!-- Columns selector -->
        <el-popover placement="bottom-end" :width="240" trigger="click">
          <template #reference>
            <el-button :icon="Grid" class="col-btn">Columns</el-button>
          </template>
          <div class="col-picker">
            <div class="col-picker-header">
              <span>Show / hide columns</span>
              <el-button text size="small" @click="resetColumns">Reset</el-button>
            </div>
            <div class="col-picker-list">
              <el-checkbox
                v-for="col in COLUMNS"
                :key="col.key"
                v-model="colVisible[col.key]"
                class="col-picker-item"
              >
                {{ col.label }}
              </el-checkbox>
            </div>
          </div>
        </el-popover>
      </div>

      <div class="table-wrap">
        <el-table
          :data="visibleRows"
          border
          stripe
          style="width: 100%"
          :header-cell-style="{ background: '#f5f5f5', fontWeight: '600' }"
          row-key="rowKey"
        >
          <!-- Diff status badge -->
          <el-table-column label="Diff Status" width="120" fixed="left">
            <template #default="{ row }">
              <el-tag :type="statusType(row.diffStatus)" size="small" class="status-tag">
                {{ row.diffStatus }}
              </el-tag>
            </template>
          </el-table-column>

          <!-- Changed fields summary -->
          <el-table-column label="Changed Fields" width="220" fixed="left">
            <template #default="{ row }">
              <span v-if="row.diffStatus === 'Modified' && row.changedFieldKeys?.length" class="changed-fields">
                {{ changedLabels(row) }}
              </span>
              <span v-else class="no-change">—</span>
            </template>
          </el-table-column>

          <!-- Dynamic data columns -->
          <template v-for="col in COLUMNS" :key="col.key">
            <el-table-column
              v-if="colVisible[col.key]"
              :label="col.label"
              :width="col.width"
              show-overflow-tooltip
            >
              <template #default="{ row }">
                <template v-if="isFieldChanged(row, col.key)">
                  <span class="old-val">{{ displayVal(row.baseEntry?.[col.key]) }}</span>
                  <span class="diff-arrow"> → </span>
                  <span class="new-val">{{ displayVal(row.entry[col.key]) }}</span>
                </template>
                <template v-else>
                  {{ displayVal(row.entry[col.key]) }}
                </template>
              </template>
            </el-table-column>
          </template>
        </el-table>
      </div>

      <p class="row-count">Showing {{ visibleRows.length }} of {{ allRows.length }} rows</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { ArrowLeft, Grid } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { snapshotApi } from "@/services/api";
import type { Entry, Snapshot, ChildImpact } from "@/types";

const router = useRouter();
const route = useRoute();

const loading = ref(true);
const error = ref("");
const activeTab = ref("all");

const baseSnap = ref<Snapshot | null>(null);
const compareSnap = ref<Snapshot | null>(null);
const baseEntries = ref<Entry[]>([]);
const compareEntries = ref<Entry[]>([]);

// ─── Column config ────────────────────────────────────────────────────────────
const COLUMNS = [
  { key: "division",      label: "Division",      width: 130 },
  { key: "ibpStep",       label: "IBP Step",       width: 150 },
  { key: "country",       label: "Country",        width: 120 },
  { key: "channel",       label: "Channel",        width: 130 },
  { key: "subChannel",    label: "Sub Channel",    width: 140 },
  { key: "account",       label: "Account",        width: 160 },
  { key: "brand",         label: "Brand",          width: 150 },
  { key: "rAndO",         label: "R&O",            width: 110 },
  { key: "probability",   label: "Probability",    width: 120 },
  { key: "description",   label: "Description",    width: 220 },
  { key: "categorisation",label: "Category",       width: 160 },
  { key: "impactPeriod",  label: "Impact Period",  width: 130 },
  { key: "impactYear",    label: "Impact Year",    width: 120 },
  { key: "nsvAud",        label: "NSV AUD",        width: 140 },
  { key: "nsvNzd",        label: "NSV NZD",        width: 140 },
  { key: "volumeLitres",  label: "Volume (L)",     width: 140 },
  { key: "impactType",    label: "Impact Type",    width: 140 },
  { key: "owner",         label: "Owner",          width: 180 },
  { key: "status",        label: "Entry Status",   width: 160 },
] as const;

type ColKey = (typeof COLUMNS)[number]["key"];

const DEFAULT_VISIBLE: Record<ColKey, boolean> = {
  division: true, ibpStep: true, country: true, channel: true,
  subChannel: true, account: true, brand: true, rAndO: true,
  probability: true, description: false, categorisation: true,
  impactPeriod: true, impactYear: true, nsvAud: true, nsvNzd: true,
  volumeLitres: true, impactType: true, owner: true, status: true,
};

const colVisible = reactive<Record<ColKey, boolean>>({ ...DEFAULT_VISIBLE });

function resetColumns() {
  Object.assign(colVisible, DEFAULT_VISIBLE);
}

// ─── Diff types ───────────────────────────────────────────────────────────────
interface DiffRow {
  rowKey: string;
  diffStatus: "New" | "Deleted" | "Modified" | "Unchanged";
  changedFieldKeys?: string[];
  isChild: boolean;
  entry: Record<string, unknown>;
  baseEntry?: Record<string, unknown>;
}

interface DiffResult {
  added: DiffRow[];
  deleted: DiffRow[];
  modified: DiffRow[];
  unchanged: DiffRow[];
}

// ─── Helpers ──────────────────────────────────────────────────────────────────
function strVal(v: unknown): string {
  if (v === null || v === undefined) return "";
  if (Array.isArray(v)) return v.join(",");
  return String(v);
}

function displayVal(v: unknown): string {
  if (v === null || v === undefined || v === "") return "—";
  if (Array.isArray(v)) return v.join(", ");
  return String(v);
}

function fieldLabel(key: string): string {
  return COLUMNS.find((c) => c.key === key)?.label ?? key;
}

function changedLabels(row: DiffRow): string {
  return (row.changedFieldKeys ?? []).map(fieldLabel).join(", ");
}

function isFieldChanged(row: DiffRow, key: string): boolean {
  return row.diffStatus === "Modified" && (row.changedFieldKeys ?? []).includes(key);
}

// ─── Fields to diff ───────────────────────────────────────────────────────────
const PARENT_FIELDS: (keyof Entry)[] = [
  "division", "ibpStep", "country", "channel", "subChannel", "account",
  "brand", "brandFamily", "rAndO", "probability", "categorisation",
  "description", "impactPeriod", "impactYear", "nsvAud", "nsvNzd",
  "volumeLitres", "impactType", "owner", "status",
];

const CHILD_FIELDS: (keyof ChildImpact)[] = ["nsvAud", "nsvNzd", "volumeLitres"];

function diffParentKeys(base: Entry, cmp: Entry): string[] {
  return PARENT_FIELDS.filter((f) => strVal(base[f]) !== strVal(cmp[f]));
}

function diffChildKeys(base: ChildImpact, cmp: ChildImpact): string[] {
  return CHILD_FIELDS.filter((f) => strVal(base[f]) !== strVal(cmp[f]));
}

// ─── Entry → flat record ──────────────────────────────────────────────────────
function entryMeta(e: Entry): Record<string, unknown> {
  return {
    division: e.division, ibpStep: e.ibpStep, country: e.country,
    channel: e.channel, subChannel: e.subChannel, account: e.account,
    brand: e.brand, rAndO: e.rAndO, probability: e.probability,
    description: e.description, categorisation: e.categorisation,
    impactPeriod: e.impactPeriod, impactYear: e.impactYear,
    nsvAud: e.nsvAud, nsvNzd: e.nsvNzd, volumeLitres: e.volumeLitres,
    impactType: e.impactType, owner: e.owner, status: e.status,
  };
}

function childMeta(c: ChildImpact): Record<string, unknown> {
  return { impactPeriod: c.impactPeriod, impactYear: c.impactYear, nsvAud: c.nsvAud, nsvNzd: c.nsvNzd, volumeLitres: c.volumeLitres };
}

function childKey(c: ChildImpact) {
  return `${c.impactPeriod}|${c.impactYear}`;
}

// ─── Diff child impacts ───────────────────────────────────────────────────────
function diffChildImpacts(
  parentMeta: Record<string, unknown>,
  baseChildren: ChildImpact[],
  cmpChildren: ChildImpact[],
  parentKey: number
): DiffRow[] {
  const rows: DiffRow[] = [];
  const baseMap = new Map<string, ChildImpact>();
  const cmpMap = new Map<string, ChildImpact>();
  for (const c of baseChildren) baseMap.set(childKey(c), c);
  for (const c of cmpChildren) cmpMap.set(childKey(c), c);

  const allKeys = new Set([...baseMap.keys(), ...cmpMap.keys()]);
  for (const key of allKeys) {
    const b = baseMap.get(key);
    const c = cmpMap.get(key);
    const current = c ?? b!;
    const row: DiffRow = {
      rowKey: `${parentKey}-child-${key}`,
      isChild: true,
      diffStatus: "Unchanged",
      entry: { ...parentMeta, ...childMeta(current) },
    };

    if (!b) {
      row.diffStatus = "New";
    } else if (!c) {
      row.diffStatus = "Deleted";
      row.entry = { ...parentMeta, ...childMeta(b) };
    } else {
      const changedFieldKeys = diffChildKeys(b, c);
      if (changedFieldKeys.length > 0) {
        row.diffStatus = "Modified";
        row.changedFieldKeys = changedFieldKeys;
        row.entry = { ...parentMeta, ...childMeta(c) };
        row.baseEntry = { ...parentMeta, ...childMeta(b) };
      }
    }
    rows.push(row);
  }
  return rows;
}

// ─── Main diff ────────────────────────────────────────────────────────────────
const diffResult = computed<DiffResult | null>(() => {
  if (!baseEntries.value.length && !compareEntries.value.length) return null;

  const baseMap = new Map<number, Entry>();
  const cmpMap = new Map<number, Entry>();
  for (const e of baseEntries.value) baseMap.set(e.originalEntryId ?? e.id, e);
  for (const e of compareEntries.value) cmpMap.set(e.originalEntryId ?? e.id, e);

  const added: DiffRow[] = [];
  const deleted: DiffRow[] = [];
  const modified: DiffRow[] = [];
  const unchanged: DiffRow[] = [];

  const allKeys = new Set([...baseMap.keys(), ...cmpMap.keys()]);

  for (const key of allKeys) {
    const b = baseMap.get(key);
    const c = cmpMap.get(key);
    const hasChildren = (b?.childImpacts?.length ?? 0) > 0 || (c?.childImpacts?.length ?? 0) > 0;

    if (!b) {
      // New
      if (hasChildren) {
        for (const cr of diffChildImpacts(entryMeta(c!), [], c!.childImpacts ?? [], key)) {
          added.push({ ...cr, diffStatus: "New" });
        }
      } else {
        added.push({ rowKey: `added-${key}`, diffStatus: "New", isChild: false, entry: entryMeta(c!) });
      }
    } else if (!c) {
      // Deleted
      if (hasChildren) {
        for (const cr of diffChildImpacts(entryMeta(b), b.childImpacts ?? [], [], key)) {
          deleted.push({ ...cr, diffStatus: "Deleted" });
        }
      } else {
        deleted.push({ rowKey: `deleted-${key}`, diffStatus: "Deleted", isChild: false, entry: entryMeta(b) });
      }
    } else {
      // Both present
      if (hasChildren) {
        const childRows = diffChildImpacts(entryMeta(c), b.childImpacts ?? [], c.childImpacts ?? [], key);
        for (const cr of childRows) {
          if (cr.diffStatus === "New") added.push(cr);
          else if (cr.diffStatus === "Deleted") deleted.push(cr);
          else if (cr.diffStatus === "Modified") modified.push(cr);
          else unchanged.push(cr);
        }
      } else {
        const changedFieldKeys = diffParentKeys(b, c);
        if (changedFieldKeys.length > 0) {
          modified.push({
            rowKey: `modified-${key}`,
            diffStatus: "Modified",
            changedFieldKeys,
            isChild: false,
            entry: entryMeta(c),
            baseEntry: entryMeta(b),
          });
        } else {
          unchanged.push({ rowKey: `unchanged-${key}`, diffStatus: "Unchanged", isChild: false, entry: entryMeta(c) });
        }
      }
    }
  }

  return { added, deleted, modified, unchanged };
});

// ─── Row filtering ────────────────────────────────────────────────────────────
const allRows = computed<DiffRow[]>(() => {
  if (!diffResult.value) return [];
  const { deleted, added, modified, unchanged } = diffResult.value;
  return [...deleted, ...added, ...modified, ...unchanged];
});

const visibleRows = computed<DiffRow[]>(() => {
  if (!diffResult.value) return [];
  const tab = activeTab.value;
  if (tab === "deleted") return diffResult.value.deleted;
  if (tab === "added") return diffResult.value.added;
  if (tab === "modified") return diffResult.value.modified;
  if (tab === "unchanged") return diffResult.value.unchanged;
  return allRows.value;
});

function statusType(s: string) {
  if (s === "New") return "success";
  if (s === "Deleted") return "danger";
  if (s === "Modified") return "warning";
  return "info";
}

// ─── Load data ────────────────────────────────────────────────────────────────
async function load() {
  const baseId = Number(route.query.base);
  const compareId = Number(route.query.compare);
  if (!baseId || !compareId) {
    error.value = "Invalid snapshot IDs in URL";
    loading.value = false;
    return;
  }
  loading.value = true;
  try {
    const [baseDetail, cmpDetail] = await Promise.all([
      snapshotApi.getEntries(baseId),
      snapshotApi.getEntries(compareId),
    ]);
    baseSnap.value = { id: baseDetail.id, period: baseDetail.period, year: baseDetail.year, ibpStep: baseDetail.ibpStep, createdBy: baseDetail.createdBy, createdAt: baseDetail.createdAt, entryCount: baseDetail.entryCount };
    compareSnap.value = { id: cmpDetail.id, period: cmpDetail.period, year: cmpDetail.year, ibpStep: cmpDetail.ibpStep, createdBy: cmpDetail.createdBy, createdAt: cmpDetail.createdAt, entryCount: cmpDetail.entryCount };
    baseEntries.value = baseDetail.entries;
    compareEntries.value = cmpDetail.entries;
  } catch {
    ElMessage.error("Failed to load snapshots for comparison");
    error.value = "Failed to load snapshots";
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>

<style scoped>
.page-container {
  max-width: 1600px;
  margin: 0 auto;
  padding: 24px 32px;
}

.page-header {
  margin-bottom: 28px;
}

.back-btn {
  padding-left: 0;
  color: var(--text-secondary);
  margin-bottom: 16px;
}

.header-main {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 16px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 6px;
  color: var(--text-primary);
  line-height: 1.2;
}

.page-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.snap-label {
  display: inline-block;
  padding: 1px 8px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 12px;
}
.base-label    { background: #e8f4ff; color: #0068c8; }
.compare-label { background: #f0f9eb; color: #67c23a; }

.summary-pills {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
}

.pill {
  font-size: 14px;
  padding: 0 14px;
  height: 36px;
  line-height: 36px;
}

.pill-num {
  font-size: 18px;
  font-weight: 700;
  margin-right: 4px;
}

/* Toolbar row: tabs left, Columns button right */
.toolbar-row {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 0;
}

.result-tabs {
  flex: 1;
  margin-bottom: 0;
}

.col-btn {
  margin-bottom: 2px;
  flex-shrink: 0;
}

/* Column picker popover content */
.col-picker {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.col-picker-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.col-picker-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 320px;
  overflow-y: auto;
}

.col-picker-item {
  font-size: 13px;
  margin: 0;
}

/* Table */
.table-wrap {
  overflow-x: auto;
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.status-tag {
  font-weight: 600;
}

.changed-fields {
  font-size: 12px;
  color: var(--el-color-warning-dark-2);
  line-height: 1.4;
}

.no-change {
  color: var(--text-muted, #bbb);
}

/* Old → New diff display */
.old-val {
  color: var(--el-color-danger);
  text-decoration: line-through;
  opacity: 0.75;
  font-size: 12px;
}

.diff-arrow {
  color: var(--text-muted, #999);
  font-size: 12px;
  margin: 0 2px;
}

.new-val {
  color: var(--el-color-success-dark-2);
  font-weight: 600;
  font-size: 12px;
}

.row-count {
  margin-top: 12px;
  font-size: 13px;
  color: var(--text-secondary);
}
</style>
