<template>
  <el-form
    ref="formRef"
    :model="formData"
    :rules="rules"
    label-width="140px"
    label-position="top"
  >
    <el-divider content-position="left">Entry Owner</el-divider>
    <el-row :gutter="16">
      <el-col :span="12">
        <el-form-item label="Creator" prop="creator">
          <el-input v-model="formData.creator" disabled />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="Owner" prop="owner">
          <el-select v-model="formData.owner" style="width: 100%" filterable>
            <el-option
              v-for="u in ownerOptions"
              :key="u.email"
              :value="u.email"
              :label="u.display_name ? `${u.display_name} (${u.email})` : u.email"
            />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>

    <el-divider content-position="left">Creation Period</el-divider>
    <el-row :gutter="16">
      <el-col :span="12">
        <el-form-item label="Period" prop="creationDatePeriod">
          <el-select v-model="formData.creationDatePeriod" style="width: 100%">
            <el-option v-for="p in PERIODS" :key="p" :value="p" :label="p" />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="Year" prop="creationDateYear">
          <el-select v-model="formData.creationDateYear" style="width: 100%">
            <el-option v-for="y in yearOptions" :key="y" :value="String(y)" :label="String(y)" />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>

    <el-divider content-position="left">Add to Forecast By</el-divider>
    <el-row :gutter="16">
      <el-col :span="12">
        <el-form-item label="Period" prop="addToForecastByPeriod">
          <el-select v-model="formData.addToForecastByPeriod" style="width: 100%">
            <el-option v-for="p in PERIODS" :key="p" :value="p" :label="p" />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="Year" prop="addToForecastByYear">
          <el-select v-model="formData.addToForecastByYear" style="width: 100%">
            <el-option v-for="y in yearOptions" :key="y" :value="String(y)" :label="String(y)" />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>

    <el-divider content-position="left">Organisation</el-divider>
    <el-row :gutter="16">
      <el-col :span="8">
        <el-form-item label="Division" prop="division">
          <el-select v-model="formData.division" style="width: 100%">
            <el-option v-for="d in divisionOptions" :key="d" :value="d" :label="d" />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="IBP Step" prop="ibpStep">
          <el-select v-model="formData.ibpStep" style="width: 100%">
            <el-option v-for="d in ibpStepOptions" :key="d" :value="d" :label="d" />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="Country" prop="country">
          <el-select v-model="formData.country" style="width: 100%">
            <el-option v-for="c in countryOptions" :key="c" :value="c" :label="c" />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>

    <el-divider content-position="left">Customer</el-divider>
    <el-row :gutter="16">
      <el-col :span="8">
        <el-form-item label="Channel" prop="channel">
          <el-select v-model="formData.channel" style="width: 100%">
            <el-option v-for="c in channelOptions" :key="c" :value="c" :label="c" />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="Sub-Channel" prop="subChannel">
          <el-select v-model="formData.subChannel" style="width: 100%">
            <el-option v-for="s in subChannelOptions" :key="s" :value="s" :label="s" />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="Account" prop="account">
          <el-select v-model="formData.account" style="width: 100%" clearable>
            <el-option v-for="a in accountOptions" :key="a" :value="a" :label="a" />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>

    <el-divider content-position="left">Product</el-divider>
    <el-row :gutter="16">
      <el-col :span="12">
        <el-form-item label="Brand" prop="brand">
          <el-select v-model="formData.brand" style="width: 100%">
            <el-option v-for="b in brandOptions" :key="b" :value="b" :label="b" />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="Brand Family" prop="brandFamily">
          <el-select v-model="formData.brandFamily" style="width: 100%" clearable>
            <el-option v-for="b in brandFamilyOptions" :key="b" :value="b" :label="b" />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>

    <el-divider content-position="left">Risk & Opportunity</el-divider>
    <el-row :gutter="16">
      <el-col :span="8">
        <el-form-item label="R&O Type" prop="rAndO">
          <el-radio-group v-model="formData.rAndO">
            <el-radio-button value="Risk">Risk</el-radio-button>
            <el-radio-button value="Opportunity">Opportunity</el-radio-button>
          </el-radio-group>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="Probability" prop="probability">
          <el-radio-group v-model="formData.probability">
            <el-radio-button v-for="p in probabilityOptions" :key="p" :value="p">{{ p }}</el-radio-button>
          </el-radio-group>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="Categorisation" prop="categorisation" :required="categActive">
          <el-select
            v-model="formData.categorisation"
            style="width: 100%"
            :disabled="!categActive"
            :placeholder="categActive ? 'Select' : 'Only available for Portfolio Review, Demand Review, Supply Review, or Pre-Exec Review'"
          >
            <el-option v-for="c in categOptions" :key="c" :value="c" :label="c" />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>
    <el-form-item label="Description of Risk / Opportunity" prop="description" style="margin-top: 12px">
      <el-input v-model="formData.description" type="textarea" :rows="3" />
    </el-form-item>

    <el-divider content-position="left">Impact Details</el-divider>

    <!-- Impact Type selector -->
    <el-row :gutter="16" style="margin-bottom: 16px">
      <el-col :span="24">
        <div class="impact-field-label">Impact Type <span class="impact-required">*</span></div>
        <el-radio-group v-model="formData.impactType" style="margin-top: 8px">
          <el-radio-button value="NSV">NSV</el-radio-button>
          <el-radio-button value="OI">OI</el-radio-button>
        </el-radio-group>
      </el-col>
    </el-row>

    <!-- Impact locked until Country is selected -->
    <div v-if="!formData.country" class="impact-locked">
      <el-icon><InfoFilled /></el-icon>
      Please select a Country first to enable Impact Details.
    </div>

    <!-- Impact card -->
    <div v-else class="impact-card">
      <!-- Period / Year row -->
      <el-row :gutter="16">
        <el-col :span="12">
          <div class="impact-field-label">Period</div>
          <el-select v-model="formData.impactPeriod" :disabled="hasChildImpacts" style="width: 100%; margin-top: 8px">
            <el-option v-for="p in PERIODS" :key="p" :value="p" :label="p" />
          </el-select>
        </el-col>
        <el-col :span="12">
          <div class="impact-field-label">Year</div>
          <el-select v-model="formData.impactYear" :disabled="hasChildImpacts" style="width: 100%; margin-top: 8px">
            <el-option v-for="y in yearOptions" :key="y" :value="String(y)" :label="String(y)" />
          </el-select>
        </el-col>
      </el-row>

      <!-- NSV row (required) -->
      <el-row :gutter="16" style="margin-top: 14px">
        <el-col :span="24">
          <div class="impact-field-label">{{ nsvLabel }} <span class="impact-required">*</span></div>
        </el-col>
        <el-col :span="24" style="margin-top: 8px">
          <el-input
            :model-value="formData.impactValue"
            :disabled="hasChildImpacts"
            placeholder="Enter NSV value"
            @input="formData.impactValue = cleanNumStr($event as string)"
            @blur="formData.impactValue = formatNumStr(formData.impactValue)"
            @focus="formData.impactValue = cleanNumStr(formData.impactValue)"
          />
        </el-col>
      </el-row>

      <!-- Volume row (optional) -->
      <el-row :gutter="16" style="margin-top: 14px">
        <el-col :span="24">
          <div class="impact-field-label">{{ volumeLabel }} <span style="color: var(--text-muted); font-weight:400">(optional)</span></div>
        </el-col>
        <el-col :span="24" style="margin-top: 8px">
          <el-input
            :model-value="formData.volumeValue"
            :disabled="hasChildImpacts"
            placeholder="Enter volume value (optional)"
            @input="formData.volumeValue = cleanNumStr($event as string)"
            @blur="formData.volumeValue = formatNumStr(formData.volumeValue)"
            @focus="formData.volumeValue = cleanNumStr(formData.volumeValue)"
          />
        </el-col>
      </el-row>

      <div class="impact-add-btn">
        <el-button plain @click="addChild">+ Add Impact</el-button>
      </div>
    </div>

    <!-- Prorated impact generator -->
    <div v-if="formData.country" class="prorated-card">
      <div class="prorated-title">Generate Prorated Impacts</div>
      <el-row :gutter="16" style="margin-top: 12px">
        <!-- Left: period range -->
        <el-col :span="12">
          <div class="impact-field-label">From Period</div>
          <el-row :gutter="8" style="margin-top: 8px">
            <el-col :span="12">
              <el-select v-model="prorated.fromPeriod" style="width: 100%">
                <el-option v-for="p in PERIODS" :key="p" :value="p" :label="p" />
              </el-select>
            </el-col>
            <el-col :span="12">
              <el-select v-model="prorated.fromYear" style="width: 100%">
                <el-option v-for="y in yearOptions" :key="y" :value="String(y)" :label="String(y)" />
              </el-select>
            </el-col>
          </el-row>
          <div class="impact-field-label" style="margin-top: 12px">To Period</div>
          <el-row :gutter="8" style="margin-top: 8px">
            <el-col :span="12">
              <el-select v-model="prorated.toPeriod" style="width: 100%">
                <el-option v-for="p in PERIODS" :key="p" :value="p" :label="p" />
              </el-select>
            </el-col>
            <el-col :span="12">
              <el-select v-model="prorated.toYear" style="width: 100%">
                <el-option v-for="y in yearOptions" :key="y" :value="String(y)" :label="String(y)" />
              </el-select>
            </el-col>
          </el-row>
        </el-col>
        <!-- Right: total values -->
        <el-col :span="12">
          <div class="impact-field-label">{{ nsvLabel }} Total <span class="impact-required">*</span></div>
          <el-input
            style="margin-top: 8px"
            :model-value="prorated.nsvValue"
            placeholder="Enter total value"
            @input="prorated.nsvValue = cleanNumStr($event as string)"
            @blur="prorated.nsvValue = formatNumStr(prorated.nsvValue)"
            @focus="prorated.nsvValue = cleanNumStr(prorated.nsvValue)"
          />
          <div class="impact-field-label" style="margin-top: 12px">
            {{ volumeLabel }} Total <span style="color: var(--text-muted); font-weight:400">(optional)</span>
          </div>
          <el-input
            style="margin-top: 8px"
            :model-value="prorated.volumeValue"
            placeholder="Enter total volume (optional)"
            @input="prorated.volumeValue = cleanNumStr($event as string)"
            @blur="prorated.volumeValue = formatNumStr(prorated.volumeValue)"
            @focus="prorated.volumeValue = cleanNumStr(prorated.volumeValue)"
          />
        </el-col>
      </el-row>
      <div style="text-align: right; margin-top: 16px">
        <el-button type="primary" @click="generateProrated">Generate Prorated Impacts</el-button>
      </div>
    </div>

    <!-- Child impact rows -->
    <div
      v-for="(child, idx) in formData.childImpacts"
      :key="idx"
      class="impact-child-card"
    >
      <el-row :gutter="16">
        <el-col :span="6">
          <div class="impact-field-label">Period <span class="impact-required">*</span></div>
          <el-select v-model="child.impactPeriod" placeholder="Period" style="width: 100%; margin-top: 8px">
            <el-option v-for="p in PERIODS" :key="p" :value="p" :label="p" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <div class="impact-field-label">Year</div>
          <el-select v-model="child.impactYear" style="width: 100%; margin-top: 8px">
            <el-option v-for="y in yearOptions" :key="y" :value="String(y)" :label="String(y)" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <div class="impact-field-label">{{ nsvLabel }}</div>
          <el-input
            :model-value="child.impactValue"
            placeholder="Enter value"
            style="margin-top: 8px"
            @input="child.impactValue = cleanNumStr($event as string)"
            @blur="child.impactValue = formatNumStr(child.impactValue)"
            @focus="child.impactValue = cleanNumStr(child.impactValue)"
          />
        </el-col>
        <el-col :span="6">
          <div class="impact-field-label">{{ volumeLabel }} <span style="color: var(--text-muted); font-weight:400">(optional)</span></div>
          <el-input
            :model-value="child.volumeValue"
            placeholder="Enter value"
            style="margin-top: 8px"
            @input="child.volumeValue = cleanNumStr($event as string)"
            @blur="child.volumeValue = formatNumStr(child.volumeValue)"
            @focus="child.volumeValue = cleanNumStr(child.volumeValue)"
          />
        </el-col>
      </el-row>
      <div class="impact-remove-btn">
        <el-button type="danger" link @click="removeChild(idx)">
          <el-icon><Delete /></el-icon> Remove
        </el-button>
      </div>
    </div>

  </el-form>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted, nextTick } from "vue";
import { Delete, InfoFilled } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import type { FormInstance, FormRules } from "element-plus";
import type { Entry } from "@/types";
import { PERIODS } from "@/types";
import { useLookupStore } from "@/stores/lookupStore";
import { useEntryStore } from "@/stores/entryStore";

const lookupStore = useLookupStore();
const entryStore = useEntryStore();
const currentUserEmail = computed(() => entryStore.currentUser?.email ?? "");
const ownerOptions = computed(() =>
  entryStore.users.filter((u) => u.role === 0 || u.role === 1)
);
onMounted(() => {
  lookupStore.preload();
  if (entryStore.users.length === 0) entryStore.fetchUsers();
});

const divisionOptions    = computed(() => lookupStore.getCached("division"));
const countryOptions     = computed(() => lookupStore.getCached("country"));
const channelOptions     = computed(() => lookupStore.getCached("channel"));
const probabilityOptions = computed(() => lookupStore.getCached("probability"));
const categOptions       = computed(() => lookupStore.getCached("categorisation"));
const brandOptions        = computed(() => lookupStore.getCached("brand"));
const brandFamilyOptions  = computed(() =>
  formData.value.brand
    ? lookupStore.getCached("brand_family", formData.value.brand)
    : lookupStore.getCached("brand_family")
);
const ibpStepOptions      = computed(() => lookupStore.getCached("ibp_step"));

const CATEG_ACTIVE_STEPS  = ["Portfolio Review", "Demand Review", "Supply Review", "Pre-Exec Review"];
const categActive         = computed(() => CATEG_ACTIVE_STEPS.includes(formData.value.ibpStep));

interface ChildImpactForm {
  impactYear: string;
  impactPeriod: string;
  impactValue: string;  // NSV (AUD or NZD depending on country)
  volumeValue: string;  // Volume (optional)
}

interface FormData {
  creationDatePeriod: string;
  creationDateYear: string;
  addToForecastByPeriod: string;
  addToForecastByYear: string;
  division: string;
  ibpStep: string;
  country: string;
  channel: string;
  subChannel: string;
  account: string;
  brand: string;
  brandFamily: string;
  rAndO: string;
  probability: string;
  categorisation: string;
  impactType: string;   // "NSV" | "OI"
  impactPeriod: string;
  impactYear: string;
  impactValue: string;  // NSV or OI value (AUD or NZD depending on country), required
  volumeValue: string;  // Volume, optional
  owner: string;
  creator: string;
  status: string;
  description: string;
  childImpacts: ChildImpactForm[];
}

const props = defineProps<{ entry?: Entry | null }>();

const formRef = ref<FormInstance>();
const currentYear = new Date().getFullYear();
const currentMonth = new Date().getMonth() + 1;
const currentPeriod = `F${String(currentMonth).padStart(2, "0")}`;
const yearOptions = Array.from({ length: 10 }, (_, i) => currentYear - 2 + i);

function defaultForm(): FormData {
  const email = currentUserEmail.value;
  return {
    creationDatePeriod: currentPeriod,
    creationDateYear: String(currentYear),
    addToForecastByPeriod: currentPeriod,
    addToForecastByYear: String(currentYear),
    division: "",
    ibpStep: "",
    country: "",
    channel: "",
    subChannel: "",
    account: "",
    brand: "",
    brandFamily: "",
    rAndO: "Risk",
    probability: "",
    categorisation: "",
    impactType: "NSV",
    impactPeriod: currentPeriod,
    impactYear: String(currentYear),
    impactValue: "",
    volumeValue: "",
    owner: email,
    creator: email,
    status: "Open",
    description: "",
    childImpacts: [],
  };
}

const formData = ref<FormData>(defaultForm());
const isLoadingEntry = ref(false);
const hasChildImpacts = computed(() => formData.value.childImpacts.length > 0);

// Always sync creator/owner to current user when in new-entry mode
watch(currentUserEmail, (email) => {
  if (email && !props.entry) {
    formData.value.creator = email;
    formData.value.owner = email;
  }
});

// Sub-Channel options cascade from selected Channel
const subChannelOptions = computed(() =>
  formData.value.channel
    ? lookupStore.getCached("sub_channel", formData.value.channel)
    : lookupStore.getCached("sub_channel")
);

// Account options cascade from selected Sub-Channel
const accountOptions = computed(() =>
  formData.value.subChannel
    ? lookupStore.getCached("account", formData.value.subChannel)
    : lookupStore.getCached("account")
);

watch(() => formData.value.channel, (val) => {
  if (!isLoadingEntry.value) {
    formData.value.subChannel = "";
    formData.value.account = "";
  }
  if (val) lookupStore.loadChildren("sub_channel", val);
});

watch(() => formData.value.subChannel, (val) => {
  if (!isLoadingEntry.value) formData.value.account = "";
  if (val) lookupStore.loadChildren("account", val);
});

watch(() => formData.value.brand, (val) => {
  if (!isLoadingEntry.value) formData.value.brandFamily = "";
  if (val) lookupStore.loadChildren("brand_family", val);
});

watch(() => formData.value.ibpStep, (val) => {
  if (!CATEG_ACTIVE_STEPS.includes(val)) formData.value.categorisation = "";
});

const nsvLabel = computed(() => {
  const currency = formData.value.country === "New Zealand" ? "NZD" : "AUD";
  return `${formData.value.impactType || "NSV"} (${currency})`;
});
const volumeLabel = "Volume (Cases)";

watch(
  () => props.entry,
  async (entry) => {
    if (entry) {
      isLoadingEntry.value = true;
      const isNzd = entry.country === "New Zealand";
      const nsvValue = isNzd ? (entry.nsvNzd || "") : (entry.nsvAud || "");
      formData.value = {
        creationDatePeriod: entry.creationDatePeriod || currentPeriod,
        creationDateYear: entry.creationDateYear || String(currentYear),
        addToForecastByPeriod: entry.addToForecastByPeriod || currentPeriod,
        addToForecastByYear: entry.addToForecastByYear || String(currentYear),
        division: entry.division || "",
        ibpStep: entry.ibpStep || "",
        country: entry.country || "",
        channel: entry.channel || "",
        subChannel: entry.subChannel || "",
        account: entry.account || "",
        brand: entry.brand || "",
        brandFamily: Array.isArray(entry.brandFamily)
          ? entry.brandFamily[0] ?? ""
          : entry.brandFamily ?? "",
        rAndO: entry.rAndO || "Risk",
        probability: entry.probability || "",
        categorisation: entry.categorisation || "",
        impactType: entry.impactType || "NSV",
        impactPeriod: entry.impactPeriod || "",
        impactYear: entry.impactYear || (entry.childImpacts?.length ? "" : String(currentYear)),
        impactValue: formatNumStr(nsvValue),
        volumeValue: formatNumStr(entry.volumeLitres || ""),
        owner: entry.owner || "",
        creator: entry.id === 0 ? (currentUserEmail.value || entry.creator || "") : (entry.creator || ""),
        status: entry.status || "Open",
        description: entry.description || "",
        childImpacts: (entry.childImpacts || []).map((ci) => {
          const ciNsv = isNzd ? (ci.nsvNzd || "") : (ci.nsvAud || "");
          return {
            impactYear: ci.impactYear || "",
            impactPeriod: ci.impactPeriod || "",
            impactValue: formatNumStr(ciNsv),
            volumeValue: formatNumStr(ci.volumeLitres || ""),
          };
        }),
      };
      if (entry.channel) lookupStore.loadChildren("sub_channel", entry.channel);
      if (entry.subChannel) lookupStore.loadChildren("account", entry.subChannel);
      if (entry.brand) lookupStore.loadChildren("brand_family", entry.brand);
      await nextTick();
      isLoadingEntry.value = false;
    } else {
      formData.value = defaultForm();
    }
  },
  { immediate: true }
);

const rules: FormRules = {
  creationDatePeriod: [{ required: true, message: "Required", trigger: "change" }],
  creationDateYear:   [{ required: true, message: "Required", trigger: "change" }],
  division: [{ required: true, message: "Required", trigger: "change" }],
  ibpStep: [{ required: true, message: "Required", trigger: "change" }],
  country: [{ required: true, message: "Required", trigger: "change" }],
  channel: [{ required: true, message: "Required", trigger: "change" }],
  subChannel: [{ required: true, message: "Required", trigger: "change" }],
  account: [{ required: true, message: "Required", trigger: "blur" }],
  brand: [{ required: true, message: "Required", trigger: "change" }],
  brandFamily: [{ required: true, message: "Required", trigger: "change" }],
  rAndO: [{ required: true, message: "Required", trigger: "change" }],
  probability: [{ required: true, message: "Required", trigger: "change" }],
  categorisation: [{
    validator: (_rule: unknown, value: string, callback: (e?: Error) => void) => {
      if (categActive.value && !value) callback(new Error("Required"));
      else callback();
    },
    trigger: "change",
  }],
  owner: [{ required: true, message: "Required", trigger: "change" }],
  creator: [{ required: true, message: "Required", trigger: "blur" }],
  description: [{ required: true, message: "Required", trigger: "blur" }],
};

function addChild() {
  const isFirst = formData.value.childImpacts.length === 0;
  if (isFirst) {
    formData.value.impactPeriod = "";
    formData.value.impactYear = "";
    formData.value.impactValue = "";
    formData.value.volumeValue = "";
  }
  const count = isFirst ? 2 : 1;
  for (let i = 0; i < count; i++) {
    formData.value.childImpacts.push({
      impactYear: String(currentYear),
      impactPeriod: "",
      impactValue: "",
      volumeValue: "",
    });
  }
}

function removeChild(idx: number) {
  formData.value.childImpacts.splice(idx, 1);
  if (formData.value.childImpacts.length === 1) {
    const last = formData.value.childImpacts[0];
    formData.value.impactPeriod = last.impactPeriod || currentPeriod;
    formData.value.impactYear = last.impactYear || String(currentYear);
    formData.value.impactValue = last.impactValue;
    formData.value.volumeValue = last.volumeValue;
    formData.value.childImpacts = [];
  } else if (formData.value.childImpacts.length === 0) {
    formData.value.impactPeriod = currentPeriod;
    formData.value.impactYear = String(currentYear);
  }
}

function mapToFields(nsvValue: string, volumeValue: string) {
  const isNzd = formData.value.country === "New Zealand";
  return {
    nsvAud: isNzd ? "" : nsvValue,
    nsvNzd: isNzd ? nsvValue : "",
    volumeLitres: volumeValue,
  };
}

function cleanNumStr(val: string): string {
  let s = val.replace(/,/g, "").replace(/[^\d.]/g, "");
  const d = s.indexOf(".");
  if (d !== -1) s = s.slice(0, d + 1) + s.slice(d + 1).replace(/\./g, "");
  return s;
}
function formatNumStr(val: string): string {
  const s = cleanNumStr(val);
  if (!s) return "";
  const parts = s.split(".");
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  return parts.join(".");
}

function isValidNum(val: string): boolean {
  const s = cleanNumStr(val).trim();
  return s !== "" && !isNaN(Number(s));
}

function periodToNum(period: string, year: string): number {
  return parseInt(year) * 100 + parseInt(period.slice(1));
}

async function validate() {
  try {
    await formRef.value!.validate();

    if (hasChildImpacts.value) {
      for (let i = 0; i < formData.value.childImpacts.length; i++) {
        const ci = formData.value.childImpacts[i];
        if (!ci.impactPeriod) {
          ElMessage.error(`Row ${i + 1}: Impact Period is required.`);
          return null;
        }
        if (!ci.impactYear) {
          ElMessage.error(`Row ${i + 1}: Impact Year is required.`);
          return null;
        }
        if (!ci.impactValue.trim()) {
          ElMessage.error(`Row ${i + 1}: NSV value is required.`);
          return null;
        }
        if (!isValidNum(ci.impactValue)) {
          ElMessage.error(`Row ${i + 1}: NSV must be a valid number.`);
          return null;
        }
        if (ci.volumeValue.trim() && !isValidNum(ci.volumeValue)) {
          ElMessage.error(`Row ${i + 1}: Volume must be a valid number.`);
          return null;
        }
        ci.impactValue = cleanNumStr(ci.impactValue);
        ci.volumeValue = cleanNumStr(ci.volumeValue);
      }
    } else {
      if (!formData.value.impactPeriod) {
        ElMessage.error("Impact Period is required.");
        return null;
      }
      if (!formData.value.impactYear) {
        ElMessage.error("Impact Year is required.");
        return null;
      }
      if (!formData.value.impactValue.trim()) {
        ElMessage.error("NSV value is required.");
        return null;
      }
      if (!isValidNum(formData.value.impactValue)) {
        ElMessage.error("NSV must be a valid number.");
        return null;
      }
      if (formData.value.volumeValue.trim() && !isValidNum(formData.value.volumeValue)) {
        ElMessage.error("Volume must be a valid number.");
        return null;
      }
      formData.value.impactValue = cleanNumStr(formData.value.impactValue);
      formData.value.volumeValue = cleanNumStr(formData.value.volumeValue);
    }

    // Validate all impact periods must be strictly after the forecast period
    const fPeriod = formData.value.addToForecastByPeriod;
    const fYear   = formData.value.addToForecastByYear;
    if (fPeriod && fYear) {
      const fNum = periodToNum(fPeriod, fYear);
      const invalidRows: string[] = [];
      if (hasChildImpacts.value) {
        formData.value.childImpacts.forEach((ci, i) => {
          if (ci.impactPeriod && ci.impactYear && periodToNum(ci.impactPeriod, ci.impactYear) <= fNum) {
            invalidRows.push(`Row ${i + 1} (${ci.impactPeriod}/${ci.impactYear})`);
          }
        });
      } else if (formData.value.impactPeriod && formData.value.impactYear) {
        if (periodToNum(formData.value.impactPeriod, formData.value.impactYear) <= fNum) {
          invalidRows.push(`${formData.value.impactPeriod}/${formData.value.impactYear}`);
        }
      }
      if (invalidRows.length > 0) {
        ElMessage.error(
          `Impact period must be after Add to Forecast By (${fPeriod}/${fYear}). Invalid: ${invalidRows.join(", ")}`
        );
        return null;
      }
    }

    const { nsvAud, nsvNzd, volumeLitres } = mapToFields(
      formData.value.impactValue,
      formData.value.volumeValue,
    );
    return {
      ...formData.value,
      nsvAud, nsvNzd, volumeLitres,
      childImpacts: formData.value.childImpacts.map((ci) => {
        const m = mapToFields(ci.impactValue, ci.volumeValue);
        return { impactYear: ci.impactYear, impactPeriod: ci.impactPeriod, ...m };
      }),
    };
  } catch {
    return null;
  }
}

const prorated = ref({
  fromPeriod: currentPeriod,
  fromYear: String(currentYear),
  toPeriod: "F12",
  toYear: String(currentYear),
  nsvValue: "",
  volumeValue: "",
});

function generateProrated() {
  const fromIdx = PERIODS.indexOf(prorated.value.fromPeriod);
  const toIdx   = PERIODS.indexOf(prorated.value.toPeriod);
  const fromYear = parseInt(prorated.value.fromYear);
  const toYear   = parseInt(prorated.value.toYear);

  if (fromYear > toYear || (fromYear === toYear && fromIdx > toIdx)) {
    ElMessage.error("Start period must be before or equal to end period.");
    return;
  }
  const nsvRaw = cleanNumStr(prorated.value.nsvValue);
  if (!nsvRaw || !isValidNum(nsvRaw)) {
    ElMessage.error(`Please enter a valid ${nsvLabel.value} total value.`);
    return;
  }

  const periods: { period: string; year: string }[] = [];
  for (let y = fromYear; y <= toYear; y++) {
    const pStart = y === fromYear ? fromIdx : 0;
    const pEnd   = y === toYear   ? toIdx   : PERIODS.length - 1;
    for (let p = pStart; p <= pEnd; p++) {
      periods.push({ period: PERIODS[p], year: String(y) });
    }
  }

  const nsvTotal = parseFloat(nsvRaw);
  const nsvEach  = nsvTotal / periods.length;

  const volRaw   = cleanNumStr(prorated.value.volumeValue);
  const volTotal = volRaw && isValidNum(volRaw) ? parseFloat(volRaw) : 0;
  const volEach  = volTotal > 0 ? volTotal / periods.length : 0;

  const round2 = (n: number) => String(Math.round(n * 100) / 100);

  formData.value.impactPeriod = "";
  formData.value.impactYear   = "";
  formData.value.impactValue  = "";
  formData.value.volumeValue  = "";
  formData.value.childImpacts = periods.map(({ period, year }) => ({
    impactPeriod: period,
    impactYear:   year,
    impactValue:  round2(nsvEach),
    volumeValue:  volEach > 0 ? round2(volEach) : "",
  }));

  ElMessage.success(`Generated ${periods.length} prorated impacts.`);
}

function reset() {
  formData.value = defaultForm();
  formRef.value?.clearValidate();
}

defineExpose({ validate, reset });
</script>

<style scoped>
.impact-locked {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 18px;
  border: 1px dashed var(--border-color);
  border-radius: 0.625rem;
  color: var(--text-muted);
  font-size: 13px;
  margin-bottom: 12px;
}

.impact-card {
  border: 1px solid var(--border-color);
  border-radius: 0.625rem;
  padding: 20px;
  margin-bottom: 12px;
  background: var(--bg-secondary);
}

.impact-child-card {
  border: 1px solid var(--border-color);
  border-radius: 0.625rem;
  padding: 20px;
  margin-bottom: 12px;
  background: var(--el-bg-color);
}

.impact-field-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--el-text-color-regular);
}

.impact-required {
  color: #d4183d;
}

.impact-add-btn {
  text-align: right;
  margin-top: 16px;
}

.impact-remove-btn {
  text-align: right;
  margin-top: 12px;
}

.prorated-card {
  border: 1px dashed var(--el-color-primary);
  border-radius: 0.625rem;
  padding: 20px;
  margin-bottom: 12px;
  background: var(--el-color-primary-light-9, #ecf5ff);
}

.prorated-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--el-color-primary);
}
</style>
