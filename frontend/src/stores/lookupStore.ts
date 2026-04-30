import { defineStore } from "pinia";
import { ref } from "vue";
import { lookupApi } from "@/services/api";

/** Cache key: "category" or "category:parentValue" */
function cacheKey(category: string, parentValue?: string): string {
  return parentValue ? `${category}:${parentValue}` : category;
}

export const useLookupStore = defineStore("lookup", () => {
  // Reactive cache so computed properties in components update automatically
  const cache = ref<Record<string, string[]>>({});

  /** Synchronous read from cache (returns [] if not yet loaded) */
  function getCached(category: string, parentValue?: string): string[] {
    return cache.value[cacheKey(category, parentValue)] ?? [];
  }

  /** Async load — fetches from API if not cached, then stores reactively */
  async function getOptions(category: string, parentValue?: string): Promise<string[]> {
    const key = cacheKey(category, parentValue);
    if (!cache.value[key]) {
      const values = await lookupApi.get(category, parentValue);
      cache.value[key] = values;
    }
    return cache.value[key];
  }

  /**
   * Preload all top-level (no-parent) option categories.
   * Call this once on app startup (e.g. in App.vue onMounted).
   */
  async function preload(): Promise<void> {
    const topLevel = [
      "division", "country", "channel", "sub_channel", "account",
      "brand_family", "brand", "categorisation", "probability",
      "status", "ibp_step",
    ];
    await Promise.all(topLevel.map((c) => getOptions(c)));
  }

  /** Pre-fetch child options for a given parent (call on parent selection) */
  async function loadChildren(
    childCategory: string,
    parentValue: string
  ): Promise<void> {
    await getOptions(childCategory, parentValue);
  }

  return { getCached, getOptions, preload, loadChildren };
});
