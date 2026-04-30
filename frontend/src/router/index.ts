import { createRouter, createWebHistory } from "vue-router";
import MainPage from "@/pages/MainPage.vue";
import EntryHistoryPage from "@/pages/EntryHistoryPage.vue";
import ViewSnapshotsPage from "@/pages/ViewSnapshotsPage.vue";
import SnapshotDetailPage from "@/pages/SnapshotDetailPage.vue";
import SnapshotComparisonPage from "@/pages/SnapshotComparisonPage.vue";

const routes = [
  { path: "/", component: MainPage },
  { path: "/entry/:originalEntryId/history", component: EntryHistoryPage },
  { path: "/snapshots", component: ViewSnapshotsPage },
  { path: "/snapshots/compare", component: SnapshotComparisonPage },
  { path: "/snapshots/:snapshotId", component: SnapshotDetailPage },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});
