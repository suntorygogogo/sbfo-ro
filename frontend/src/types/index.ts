export interface ChildImpact {
  id: number;
  impactYear: string;
  impactPeriod: string;
  nsvAud?: string;
  nsvNzd?: string;
  volumeLitres?: string;
}

export interface Entry {
  id: number;
  originalEntryId?: number;
  version: number;
  creationDate: string;
  creationDatePeriod?: string;
  creationDateYear?: string;
  addToForecastByPeriod?: string;
  addToForecastByYear?: string;
  division: string;
  ibpStep?: string;
  country: string;
  channel: string;
  subChannel: string;
  account: string;
  brand: string;
  brandFamily?: string | string[];
  rAndO: string;
  probability: string;
  categorisation: string;
  impactPeriod?: string;
  impactYear?: string;
  nsvAud?: string;
  nsvNzd?: string;
  volumeLitres?: string;
  impactType?: string;
  owner: string;
  creator?: string;
  modifiedUser?: string;
  lastModified?: string;
  status?: string;
  description?: string;
  childImpacts?: ChildImpact[];
}

export type UserRole =
  | "User"
  | "Department Approver"
  | "Finance Approver"
  | "System Admin";

/** 0=System Admin, 1=User, 2=Department Approver, 3=Finance Approver */
export const ROLE_MAP: Record<number, UserRole> = {
  0: "System Admin",
  1: "User",
  2: "Department Approver",
  3: "Finance Approver",
};

export interface AppUser {
  id: number;
  email: string;
  display_name?: string;
  role: number;
  departments?: string[] | null;  // null = all; array = restricted (role 2 only)
}

export const DIVISIONS = ["Alcohol", "Non-Alcohol"];
export const COUNTRIES = ["Australia", "New Zealand"];
export const CHANNELS = ["On-Premise", "Off-Premise", "Direct", "Export"];
export const SUB_CHANNELS = ["Hotel", "Restaurant", "Club", "Bar", "Supermarket", "Liquor", "Online"];
export const R_AND_O_OPTIONS = ["Risk", "Opportunity"];
export const PROBABILITY_OPTIONS = ["High", "Medium", "Low", "Very High", "Very Low"];
export const CATEGORISATION_OPTIONS = [
  "Volume",
  "Price",
  "Mix",
  "Foreign Exchange",
  "Rebates",
  "Promotions",
  "New Products",
  "Discontinued Products",
  "Other",
];
export const IMPACT_UNITS = ["AUD", "NZD", "Litres"];
export const STATUS_OPTIONS = ["Open", "Approved", "Dismissed", "Included in Forecast"];
export const PERIODS = ["F01", "F02", "F03", "F04", "F05", "F06", "F07", "F08", "F09", "F10", "F11", "F12"];
export const BRANDS = [
  "Suntory", "Jim Beam", "Maker's Mark", "Knob Creek",
  "Courvoisier", "Laphroaig", "Teacher's", "Ardmore",
  "Bowmore", "Auchentoshan", "Kilbeggan", "Other",
];
export const USER_ROLES: UserRole[] = [
  "User", "Department Approver", "Finance Approver", "System Admin",
];

export const COUNTRY_CURRENCY_MAP: Record<string, string> = {
  Australia: "AUD",
  "New Zealand": "NZD",
};

export interface Snapshot {
  id: number;
  period: string;
  year: string;
  ibpStep: string;
  createdBy: string;
  createdAt: string;
  entryCount: number;
}

export interface SnapshotDetail extends Snapshot {
  entries: Entry[];
}

