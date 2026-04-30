<template>
  <div class="page-container">
    <!-- Header -->
    <div class="page-header">
      <el-button :icon="ArrowLeft" text class="back-btn" @click="router.push('/snapshots')">
        Back to Snapshots
      </el-button>

      <div v-if="snapshot" class="header-main">
        <div class="title-row">
          <h1 class="page-title">Snapshot: {{ snapshot.ibpStep }} - {{ snapshot.period }} {{ snapshot.year }}</h1>
          <el-tag type="info" size="large" class="ibp-tag">{{ snapshot.ibpStep }}</el-tag>
        </div>
        <p class="page-meta">Created: {{ formatDate(snapshot.createdAt) }} &nbsp;·&nbsp; {{ snapshot.entryCount }} {{ snapshot.entryCount === 1 ? 'entry' : 'entries' }}</p>
      </div>
      <div v-else-if="loading" class="header-main">
        <el-skeleton :rows="1" animated style="width: 400px" />
      </div>
    </div>

    <!-- Table -->
    <div v-loading="loading">
      <EntriesTable
        v-if="!loading"
        :entries="entries"
        :snapshot-mode="true"
        :export-filename="snapshot ? `Snapshot_${snapshot.ibpStep}_${snapshot.period}_${snapshot.year}` : 'Snapshot'"
        @history="goToHistory"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { ArrowLeft } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { snapshotApi } from "@/services/api";
import type { Snapshot, Entry } from "@/types";
import EntriesTable from "@/components/EntriesTable.vue";

const router = useRouter();
const route = useRoute();

const loading = ref(true);
const snapshot = ref<Snapshot | null>(null);
const entries = ref<Entry[]>([]);

async function load() {
  const id = Number(route.params.snapshotId);
  loading.value = true;
  try {
    const detail = await snapshotApi.getEntries(id);
    snapshot.value = {
      id: detail.id,
      period: detail.period,
      year: detail.year,
      ibpStep: detail.ibpStep,
      createdBy: detail.createdBy,
      createdAt: detail.createdAt,
      entryCount: detail.entryCount,
    };
    entries.value = detail.entries;
  } catch {
    ElMessage.error("Failed to load snapshot");
  } finally {
    loading.value = false;
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

function goToHistory(entry: Entry) {
  router.push(`/entry/${entry.originalEntryId || entry.id}/history`);
}

onMounted(load);
</script>

<style scoped>
.page-container {
  max-width: 1600px;
  margin: 0 auto;
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.back-btn {
  padding-left: 0;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.header-main {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
  line-height: 1.2;
}

.ibp-tag {
  font-size: 13px;
}

.page-meta {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}
</style>
