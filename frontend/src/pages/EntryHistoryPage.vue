<template>
  <div class="page-container">
    <div class="page-nav">
      <el-button :icon="ArrowLeft" plain @click="router.push('/')">Back to Entries</el-button>
    </div>

    <div class="page-header">
      <div v-if="versions.length" class="history-header-content">
        <h1 class="page-title">Entry History</h1>

        <!-- Current Entry Info -->
        <div class="entry-info card">
          <el-row :gutter="16">
            <el-col :span="3">
              <label class="info-label">Division</label>
              <div class="info-value">{{ latestVersion?.division }}</div>
            </el-col>
            <el-col :span="3">
              <label class="info-label">Country</label>
              <div class="info-value">{{ latestVersion?.country }}</div>
            </el-col>
            <el-col :span="3">
              <label class="info-label">Brand</label>
              <div class="info-value">{{ latestVersion?.brand }}</div>
            </el-col>
            <el-col :span="6">
              <label class="info-label">Owner</label>
              <div class="info-value">{{ latestVersion?.owner }}</div>
            </el-col>
            <el-col :span="3">
              <label class="info-label">Status</label>
              <el-tag :type="statusType(latestVersion?.status)" size="small">
                {{ latestVersion?.status }}
              </el-tag>
            </el-col>
            <el-col :span="3">
              <label class="info-label">ID</label>
              <div class="info-value">{{ latestVersion?.originalEntryId }}</div>
            </el-col>
            <el-col :span="3">
              <label class="info-label">Total Versions</label>
              <div class="info-value">{{ versions.length }}</div>
            </el-col>
          </el-row>
        </div>
      </div>
    </div>

    <div v-if="loading" class="state-block">
      <el-icon :size="32" class="spin"><Loading /></el-icon>
    </div>

    <div v-else-if="!versions.length" class="state-block state-block-muted">
      No history found for this entry.
    </div>

    <el-table
      v-else
      :data="versions"
      border
      style="width: 100%; margin-top: 24px"
      :row-class-name="rowClassName"
    >
      <el-table-column type="expand">
        <template #default="{ row }">
          <div v-if="row.childImpacts?.length" class="child-details">
            <strong>Impact Details:</strong>
            <el-table :data="row.childImpacts" size="small" border style="margin-top:8px">
              <el-table-column prop="impactYear" label="Year" width="80" />
              <el-table-column prop="impactPeriod" label="Period" width="80" />
              <el-table-column label="Impact (AUD)" width="130">
                <template #default="{ row: ci }">{{ formatMoney(ci.nsvAud) }}</template>
              </el-table-column>
              <el-table-column label="Impact (NZD)" width="130">
                <template #default="{ row: ci }">{{ formatMoney(ci.nsvNzd) }}</template>
              </el-table-column>
              <el-table-column label="Volume (Cases)" width="110">
                <template #default="{ row: ci }">{{ formatVol(ci.volumeLitres) }}</template>
              </el-table-column>
            </el-table>
          </div>
          <div v-else style="padding: 8px; color: var(--text-muted)">No impact details</div>
        </template>
      </el-table-column>


      <el-table-column label="Country" width="120">
        <template #default="{ row, $index }">
          {{ row.country }}
          <el-tag v-if="hasChanged($index, 'country')" type="warning" size="small" style="margin-left:4px">Updated</el-tag>
        </template>
      </el-table-column>

      <el-table-column label="Division" width="100">
        <template #default="{ row, $index }">
          {{ row.division }}
          <el-tag v-if="hasChanged($index, 'division')" type="warning" size="small" style="margin-left:4px">Updated</el-tag>
        </template>
      </el-table-column>

      <el-table-column label="Categorisation" min-width="120">
        <template #default="{ row, $index }">
          {{ row.categorisation }}
          <el-tag v-if="hasChanged($index, 'categorisation')" type="warning" size="small" style="margin-left:4px">Updated</el-tag>
        </template>
      </el-table-column>

      <el-table-column label="NSV" width="160">
        <template #default="{ row, $index }">
          {{ formatNsvImpact(row) }}
          <el-tag v-if="hasChanged($index, 'nsvAud') || hasChanged($index, 'nsvNzd') || hasChanged($index, 'volumeLitres')" type="warning" size="small" style="margin-left:4px">Updated</el-tag>
        </template>
      </el-table-column>

      <el-table-column label="Owner" min-width="100">
        <template #default="{ row, $index }">
          {{ row.owner }}
          <el-tag v-if="hasChanged($index, 'owner')" type="warning" size="small" style="margin-left:4px">Updated</el-tag>
        </template>
      </el-table-column>

      <el-table-column label="Status" width="100">
        <template #default="{ row, $index }">
          <el-tag :type="statusType(row.status)" size="small">{{ row.status }}</el-tag>
          <el-tag v-if="hasChanged($index, 'status')" type="warning" size="small" style="margin-left:4px">Updated</el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="modifiedUser" label="Modified By" min-width="140">
        <template #default="{ row }">
          {{ row.modifiedUser || row.creator || "-" }}
        </template>
      </el-table-column>

      <el-table-column prop="lastModified" label="Modified At" width="155">
        <template #default="{ row }">
          {{ formatDate(row.lastModified) }}
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { ArrowLeft, Loading } from "@element-plus/icons-vue";
import { entryApi } from "@/services/api";
import type { Entry } from "@/types";
import { formatDate, formatMoney, formatVol } from "@/utils/formatters";

const router = useRouter();
const route = useRoute();
const loading = ref(true);
const versions = ref<Entry[]>([]);

const latestVersion = computed(() => versions.value[0]);

onMounted(async () => {
  const id = Number(route.params.originalEntryId);
  try {
    const data = await entryApi.getHistory(id);
    versions.value = data.versions;
  } finally {
    loading.value = false;
  }
});

function rowClassName({ row }: { row: Entry }) {
  return row.version === latestVersion.value?.version ? "row-latest" : "";
}

function hasChanged(index: number, field: keyof Entry): boolean {
  if (index >= versions.value.length - 1) return false;
  const current = versions.value[index];
  const prev = versions.value[index + 1];
  return JSON.stringify(current[field]) !== JSON.stringify(prev[field]);
}

function statusType(status?: string) {
  const map: Record<string, "primary" | "success" | "warning" | "danger" | "info"> = {
    Open: "primary",
    Approved: "success",
    Dismissed: "info",
    "Included in Forecast": "warning",
  };
  return map[status || "Open"] ?? "primary";
}

function formatNsvImpact(row: Entry) {
  if (row.country === "New Zealand") return formatMoney(row.nsvNzd);
  return formatMoney(row.nsvAud);
}
</script>

<style scoped>
.page-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

.page-nav {
  margin-bottom: 16px;
}

.history-header-content {
  margin-top: 4px;
}

.entry-info {
  padding: 16px;
  margin-top: 16px;
}

.info-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  display: block;
  margin-bottom: 4px;
}

.info-value {
  font-weight: 500;
  color: var(--text-primary);
}

.child-details {
  padding: 12px 24px;
}

.state-block {
  text-align: center;
  padding: 48px;
}

.state-block-muted {
  color: var(--text-muted);
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

:deep(.row-latest) td {
  background-color: #f0fdf4 !important;
}
</style>
