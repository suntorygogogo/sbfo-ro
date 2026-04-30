import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { entryApi, userApi } from "@/services/api";
import type { Entry, AppUser } from "@/types";
import { ROLE_MAP } from "@/types";

export const useEntryStore = defineStore("entry", () => {
  const entries = ref<Entry[]>([]);
  const loading = ref(false);
  const users = ref<AppUser[]>([]);
  const currentUser = ref<AppUser | null>(null);

  const userRole = computed(() =>
    currentUser.value != null ? ROLE_MAP[currentUser.value.role] ?? "User" : "User"
  );

  const filters = ref({
    division: "",
    ibpStep: "",
    country: "",
    channel: "",
    sub_channel: "",
    account: "",
    brand: "",
    brand_family: "",
    categorisation: "",
    r_and_o: "",
    probability: "",
    status: "",
    owner: "",
    creation_date_period: "",
    creation_date_year: "",
  });

  const displayEntries = computed(() => {
    const email = currentUser.value?.email ?? "";
    const isUser = userRole.value === "User";
    return entries.value
      .filter((e) => !isUser || e.owner === email || e.creator === email)
      .map((e) => ({
        ...e,
        customer: [e.channel, e.subChannel, e.account].filter(Boolean).join(" / "),
        product: [
          e.brand,
          Array.isArray(e.brandFamily)
            ? e.brandFamily.join(", ")
            : e.brandFamily,
        ]
          .filter(Boolean)
          .join(" - "),
      }));
  });

  const canCreate = computed(() =>
    ["User", "System Admin"].includes(userRole.value)
  );
  const canApprove = computed(() =>
    ["Department Approver", "Finance Approver", "System Admin"].includes(userRole.value)
  );

  async function fetchUsers() {
    users.value = await userApi.getAll();
  }

  async function fetchEntries() {
    loading.value = true;
    try {
      const activeFilters = Object.fromEntries(
        Object.entries(filters.value).filter(([, v]) => v !== "")
      );
      if (userRole.value) activeFilters.role = userRole.value;
      // Pass department restriction for Department Approver (null = all, array = restricted)
      if (userRole.value === "Department Approver") {
        const depts = currentUser.value?.departments;
        if (depts && depts.length > 0) {
          activeFilters.user_departments = depts.join(",");
        }
      }
      const data = await entryApi.getAll(activeFilters);
      entries.value = data.entries;
    } finally {
      loading.value = false;
    }
  }

  async function createEntry(data: Partial<Entry> & { childImpacts?: unknown[] }) {
    await entryApi.create(data);
    await fetchEntries();
  }

  async function updateEntry(id: number, data: Partial<Entry> & { childImpacts?: unknown[] }) {
    await entryApi.update(id, data);
    await fetchEntries();
  }

  async function deleteEntry(id: number) {
    await entryApi.delete(id, currentUser.value?.email);
    await fetchEntries();
  }

  async function approveEntry(id: number, modifiedUser?: string) {
    await entryApi.approve(id, modifiedUser);
    await fetchEntries();
  }

  function resetFilters() {
    Object.keys(filters.value).forEach((k) => {
      (filters.value as Record<string, string>)[k] = "";
    });
  }

  return {
    entries,
    loading,
    users,
    currentUser,
    userRole,
    filters,
    displayEntries,
    canCreate,
    canApprove,
    fetchUsers,
    fetchEntries,
    createEntry,
    updateEntry,
    deleteEntry,
    approveEntry,
    resetFilters,
  };
});
