<template>
  <div ref="tableWrapper" class="entries-table-wrapper">

    <!-- Quick Filters -->
    <div v-if="!isReadOnly || snapshotMode" class="quick-filters-section">
      <p class="section-label">Quick Filters</p>
      <div class="quick-filter-row">
        <button
          v-for="qf in quickFilterDefs"
          :key="qf.key"
          :class="['quick-btn', { active: quickFilters[qf.key] }]"
          @click="toggleQuick(qf.key)"
        >{{ qf.label }}</button>
      </div>
      <div class="quick-filter-row">
        <button
          v-for="dept in ibpStepOptions"
          :key="dept"
          :class="['quick-btn', { active: getFilter('ibpStep') === dept }]"
          @click="toggleIbpStep(dept)"
        >{{ dept }}</button>
      </div>
    </div>

    <!-- All Filters (collapsible) -->
    <div v-if="!isReadOnly || snapshotMode" class="all-filters-section">
      <div class="all-filters-header" @click="allFiltersOpen = !allFiltersOpen">
        <span class="all-filters-title">All Filters</span>
        <svg
          :class="['chevron-icon', { open: allFiltersOpen }]"
          viewBox="0 0 24 24" fill="none" stroke="currentColor"
          stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
        >
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </div>

      <div v-show="allFiltersOpen" class="all-filters-body">
        <!-- Row 1 -->
        <el-row :gutter="16" class="filter-row">
          <el-col :span="6">
            <label class="filter-label">Div.</label>
            <el-select :model-value="getFilter('division')" clearable placeholder="All" @update:model-value="setFilter('division', $event)">
              <el-option v-for="d in divisionOptions" :key="d" :value="d" :label="d" />
            </el-select>
          </el-col>
          <el-col :span="6">
            <label class="filter-label">Country</label>
            <el-select :model-value="getFilter('country')" clearable placeholder="All" @update:model-value="setFilter('country', $event)">
              <el-option v-for="c in countryOptions" :key="c" :value="c" :label="c" />
            </el-select>
          </el-col>
          <el-col :span="6">
            <label class="filter-label">Categorisation</label>
            <el-select :model-value="getFilter('categorisation')" clearable placeholder="All" @update:model-value="setFilter('categorisation', $event)">
              <el-option v-for="c in categOptions" :key="c" :value="c" :label="c" />
            </el-select>
          </el-col>
          <el-col :span="6">
            <label class="filter-label">Status</label>
            <el-select :model-value="getFilter('status')" clearable placeholder="All" @update:model-value="setFilter('status', $event)">
              <el-option v-for="s in statusOptions" :key="s" :value="s" :label="s" />
            </el-select>
          </el-col>
        </el-row>

        <!-- Row 2 -->
        <el-row :gutter="16" class="filter-row">
          <el-col :span="6">
            <label class="filter-label">Owner</label>
            <el-select :model-value="getFilter('owner')" clearable placeholder="All" filterable @update:model-value="setFilter('owner', $event)">
              <el-option v-for="u in ownerOptions" :key="u.email" :value="u.email" :label="u.display_name ? `${u.display_name} (${u.email})` : u.email" />
            </el-select>
          </el-col>
          <el-col :span="6">
            <label class="filter-label">IBP Step</label>
            <el-select :model-value="getFilter('ibpStep')" clearable placeholder="All" @update:model-value="setFilter('ibpStep', $event)">
              <el-option v-for="d in ibpStepOptions" :key="d" :value="d" :label="d" />
            </el-select>
          </el-col>
        </el-row>

        <!-- Customer Filters -->
        <p class="filter-group-label">Customer Filters</p>
        <el-row :gutter="16" class="filter-row">
          <el-col :span="8">
            <label class="filter-label">Channel</label>
            <el-select :model-value="getFilter('channel')" clearable placeholder="All" @update:model-value="setFilter('channel', $event)">
              <el-option v-for="c in channelOptions" :key="c" :value="c" :label="c" />
            </el-select>
          </el-col>
          <el-col :span="8">
            <label class="filter-label">Sub-Channel</label>
            <el-select :model-value="getFilter('sub_channel')" clearable placeholder="All" :disabled="!getFilter('channel')" @update:model-value="setFilter('sub_channel', $event)">
              <el-option v-for="c in subChannelOptions" :key="c" :value="c" :label="c" />
            </el-select>
          </el-col>
          <el-col :span="8">
            <label class="filter-label">Account</label>
            <el-select :model-value="getFilter('account')" clearable placeholder="All" :disabled="!getFilter('sub_channel')" @update:model-value="setFilter('account', $event)">
              <el-option v-for="a in accountOptions" :key="a" :value="a" :label="a" />
            </el-select>
          </el-col>
        </el-row>

        <!-- Product Filters -->
        <p class="filter-group-label">Product Filters</p>
        <el-row :gutter="16" class="filter-row">
          <el-col :span="12">
            <label class="filter-label">Brand</label>
            <el-select :model-value="getFilter('brand')" clearable placeholder="All" @update:model-value="setFilter('brand', $event)">
              <el-option v-for="b in brandOptions" :key="b" :value="b" :label="b" />
            </el-select>
          </el-col>
          <el-col :span="12">
            <label class="filter-label">Brand Family</label>
            <el-select :model-value="getFilter('brand_family')" clearable placeholder="All" :disabled="!getFilter('brand')" @update:model-value="setFilter('brand_family', $event)">
              <el-option v-for="b in brandFamilyOptions" :key="b" :value="b" :label="b" />
            </el-select>
          </el-col>
        </el-row>

        <div class="filter-actions">
          <el-button size="small" @click="clearFilters">Clear All Filters</el-button>
        </div>
      </div>
    </div>

    <!-- Table Toolbar -->
    <div class="table-toolbar">
      <span class="entry-count">{{ filteredEntries.length }} entries</span>
      <div class="toolbar-right" v-if="!isReadOnly || snapshotMode">
        <div class="split-view-control">
          <span class="split-view-label">Split view by:</span>
          <el-select
            v-model="splitBy"
            multiple
            collapse-tags
            collapse-tags-tooltip
            placeholder="None"
            size="small"
            style="width: 160px"
          >
            <el-option
              v-for="opt in splitByOptions"
              :key="opt.key"
              :value="opt.key"
              :label="opt.label"
            />
          </el-select>
        </div>
        <el-popover placement="bottom-end" :width="260" trigger="click">
          <template #reference>
            <el-button size="small" plain>Columns</el-button>
          </template>
          <div class="column-selector">
            <p class="column-selector-title">Visible Columns</p>
            <el-checkbox v-model="colVisible.ibpStep">IBP Step</el-checkbox>
            <el-checkbox v-model="colVisible.subChannel">Sub-Channel</el-checkbox>
            <el-checkbox v-model="colVisible.account">Account</el-checkbox>
            <el-checkbox v-model="colVisible.brandFamily">Brand Family</el-checkbox>
            <el-checkbox v-model="colVisible.description">Description</el-checkbox>
            <el-checkbox v-model="colVisible.nsvAud">Impact (AUD)</el-checkbox>
            <el-checkbox v-model="colVisible.nsvNzd">Impact (NZD)</el-checkbox>
            <el-checkbox v-model="colVisible.volumeLitres">Volume (Cases)</el-checkbox>
            <el-checkbox v-model="colVisible.impactPeriod">Impact Period</el-checkbox>
            <el-checkbox v-model="colVisible.creator">Creator</el-checkbox>
          </div>
        </el-popover>
        <div class="phased-view-control">
          <span class="phased-view-label">Period View:</span>
          <el-select v-model="phasedView" size="small" style="width: 150px">
            <el-option value="none" label="No Phased View" />
            <el-option value="month" label="Month" />
            <el-option value="quarter" label="Quarter" />
            <el-option value="half" label="Half Year" />
            <el-option value="year" label="Year" />
          </el-select>
        </div>
        <el-button size="small" plain @click="handleExport(filteredEntries)">
          <svg style="width:13px;height:13px;margin-right:4px;vertical-align:-2px" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          Export
        </el-button>
      </div>
    </div>

    <!-- Grouped view -->
    <template v-if="splitBy.length && (!isReadOnly || snapshotMode)">
      <div
        v-for="group in groupedEntries"
        :key="group.key"
        class="split-group"
      >
        <div class="split-group-header">
          <div class="split-group-breadcrumb">
            <template v-for="(item, idx) in group.breadcrumb" :key="idx">
              <span v-if="idx > 0" class="split-sep">›</span>
              <span class="split-chip">
                <span class="split-chip-label">{{ item.label }}</span>
                <span class="split-chip-val">{{ item.val }}</span>
              </span>
            </template>
          </div>
          <div class="split-header-right">
            <span class="split-count">{{ group.entries.length }} {{ group.entries.length === 1 ? 'entry' : 'entries' }}</span>
            <el-button size="small" plain @click="handleExport(group.entries, group.key)">
              <svg style="width:13px;height:13px;margin-right:4px;vertical-align:-2px" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
              Export CSV
            </el-button>
          </div>
        </div>
        <el-table
          :data="toTreeRows(group.entries)"
          border
          stripe
          row-key="_id"
          :tree-props="{ children: 'children' }"
          style="width: 100%"
          :row-class-name="rowClassName"
        >
          <el-table-column width="44" class-name="tree-toggle-col" />
          <el-table-column label="Division" width="90" align="center">
            <template #default="{ row }">
              <el-tooltip :content="row.division" placement="top">
                <span style="font-size:16px; cursor:default;">{{ divisionEmoji(row.division) }}</span>
              </el-tooltip>
            </template>
          </el-table-column>
          <el-table-column v-if="colVisible.ibpStep" prop="ibpStep" label="IBP Step" width="160" />
          <el-table-column label="Country" width="90" align="center">
            <template #default="{ row }">
              <el-tooltip :content="row.country" placement="top">
                <span>{{ countryAbbr(row.country) }}</span>
              </el-tooltip>
            </template>
          </el-table-column>
          <el-table-column prop="channel" label="Channel" width="120" />
          <el-table-column v-if="colVisible.subChannel" prop="subChannel" label="Sub-Channel" width="130" />
          <el-table-column v-if="colVisible.account" prop="account" label="Account" width="160" />
          <el-table-column prop="brand" label="Brand" width="130" />
          <el-table-column v-if="colVisible.brandFamily" prop="brandFamily" label="Brand Family" width="160">
            <template #default="{ row }">{{ Array.isArray(row.brandFamily) ? row.brandFamily.join(", ") : row.brandFamily }}</template>
          </el-table-column>
          <el-table-column prop="rAndO" label="R&O" width="120">
            <template #default="{ row }">
              <el-tag :type="row.rAndO === 'Risk' ? 'danger' : 'success'" size="small">{{ row.rAndO }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="Probability" width="110" align="center">
            <template #default="{ row }">
              <el-tooltip :content="row.probability" placement="top">
                <span :class="['prob-badge', `prob-${(row.probability || '').toLowerCase()}`]">
                  {{ (row.probability || '').charAt(0).toUpperCase() }}
                </span>
              </el-tooltip>
            </template>
          </el-table-column>
          <el-table-column v-if="colVisible.description" prop="description" label="Description" width="200" />
          <el-table-column prop="categorisation" label="Category" width="160" />
          <el-table-column prop="impactType" label="Impact Type" width="110" />
          <el-table-column label="Impact" width="150">
            <template #default="{ row }">{{ formatNsvImpact(row) }}</template>
          </el-table-column>
          <el-table-column v-if="colVisible.nsvAud" label="Impact (AUD)" width="120">
            <template #default="{ row }">{{ formatMoney(sumChildField(row, 'nsvAud')) }}</template>
          </el-table-column>
          <el-table-column v-if="colVisible.nsvNzd" label="Impact (NZD)" width="120">
            <template #default="{ row }">{{ formatMoney(sumChildField(row, 'nsvNzd')) }}</template>
          </el-table-column>
          <el-table-column v-if="colVisible.volumeLitres" label="Volume (Cases)" width="110">
            <template #default="{ row }">{{ formatVol(sumChildField(row, 'volumeLitres')) }}</template>
          </el-table-column>
          <el-table-column v-if="colVisible.impactPeriod" label="Impact Period" width="200">
            <template #default="{ row }">{{ formatImpactPeriod(row) }}</template>
          </el-table-column>
          <el-table-column
            v-for="col in phasedColumns"
            :key="col.key"
            :label="col.label"
            :width="col.width"
            align="right"
            class-name="phased-col"
          >
            <template #default="{ row }">{{ getPhasedValue(row, col) }}</template>
          </el-table-column>
          <el-table-column prop="owner" label="Owner" width="180" />
          <el-table-column v-if="colVisible.creator" prop="creator" label="Creator" width="180" />
          <el-table-column prop="status" label="Status" width="190" min-width="190">
            <template #default="{ row }">
              <el-select v-if="!snapshotMode && canEditStatusRow(row) && !(row as any)._isChild" :model-value="row.status" size="small" style="width: 170px" @change="(val: string) => handleStatusChange(row, val)">
                <el-option v-for="s in allowedStatusRow(row)" :key="s" :value="s" :label="s" />
              </el-select>
              <el-tag v-else :type="statusType(row.status)" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="lastModified" label="Last Modified" width="155">
            <template #default="{ row }">{{ formatDate(row.lastModified) }}</template>
          </el-table-column>
          <el-table-column label="Actions" width="140" align="center">
            <template #default="{ row }">
              <div v-if="!(row as any)._isChild" class="action-btns">
                <button class="action-icon" @click="$emit('history', row)" title="View History">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                </button>
                <button v-if="!snapshotMode && store.canCreate" class="action-icon" @click="$emit('duplicate', row)" title="Duplicate">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                </button>
                <button v-if="!snapshotMode && canEditRow(row)" class="action-icon" @click="handleEditClick(row)" title="Edit">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                </button>
                <el-popconfirm v-if="!snapshotMode && canDeleteRow(row)" title="Delete all versions of this entry?" confirm-button-type="danger" @confirm="$emit('delete', row)">
                  <template #reference>
                    <button class="action-icon action-icon--danger" title="Delete">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>
                    </button>
                  </template>
                </el-popconfirm>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </template>

    <!-- Flat table (no split or read-only) -->
    <el-table
      v-else
      :data="treeData"
      v-loading="isReadOnly ? false : store.loading"
      border
      stripe
      row-key="_id"
      :tree-props="{ children: 'children' }"
      style="width: 100%"
      :row-class-name="rowClassName"
    >
      <el-table-column width="44" class-name="tree-toggle-col" />
      <el-table-column label="Division" width="90" align="center">
        <template #default="{ row }">
          <el-tooltip :content="row.division" placement="top">
            <span style="font-size:16px; cursor:default;">{{ divisionEmoji(row.division) }}</span>
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column v-if="colVisible.ibpStep" prop="ibpStep" label="IBP Step" width="160" />
      <el-table-column label="Country" width="90" align="center">
        <template #default="{ row }">
          <el-tooltip :content="row.country" placement="top">
            <span>{{ countryAbbr(row.country) }}</span>
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column prop="channel" label="Channel" width="120" />
      <el-table-column v-if="colVisible.subChannel" prop="subChannel" label="Sub-Channel" width="130" />
      <el-table-column v-if="colVisible.account" prop="account" label="Account" width="160" />
      <el-table-column prop="brand" label="Brand" width="130" />
      <el-table-column v-if="colVisible.brandFamily" prop="brandFamily" label="Brand Family" width="160">
        <template #default="{ row }">
          {{ Array.isArray(row.brandFamily) ? row.brandFamily.join(", ") : row.brandFamily }}
        </template>
      </el-table-column>
      <el-table-column prop="rAndO" label="R&O" width="120">
        <template #default="{ row }">
          <el-tag :type="row.rAndO === 'Risk' ? 'danger' : 'success'" size="small">{{ row.rAndO }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="Probability" width="110" align="center">
        <template #default="{ row }">
          <el-tooltip :content="row.probability" placement="top">
            <span :class="['prob-badge', `prob-${(row.probability || '').toLowerCase()}`]">
              {{ (row.probability || '').charAt(0).toUpperCase() }}
            </span>
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column v-if="colVisible.description" prop="description" label="Description" width="200" />
      <el-table-column prop="categorisation" label="Category" width="160" />
      <el-table-column prop="impactType" label="Impact Type" width="110" />
      <el-table-column label="Impact" width="150">
        <template #default="{ row }">{{ formatNsvImpact(row) }}</template>
      </el-table-column>
      <el-table-column v-if="colVisible.nsvAud" label="Impact (AUD)" width="120">
        <template #default="{ row }">{{ formatMoney(sumChildField(row, 'nsvAud')) }}</template>
      </el-table-column>
      <el-table-column v-if="colVisible.nsvNzd" label="Impact (NZD)" width="120">
        <template #default="{ row }">{{ formatMoney(sumChildField(row, 'nsvNzd')) }}</template>
      </el-table-column>
      <el-table-column v-if="colVisible.volumeLitres" label="Volume (Cases)" width="110">
        <template #default="{ row }">{{ formatVol(sumChildField(row, 'volumeLitres')) }}</template>
      </el-table-column>
      <el-table-column v-if="colVisible.impactPeriod" label="Impact Period" width="200">
        <template #default="{ row }">{{ formatImpactPeriod(row) }}</template>
      </el-table-column>
      <el-table-column
        v-for="col in phasedColumns"
        :key="col.key"
        :label="col.label"
        :width="col.width"
        align="right"
        class-name="phased-col"
      >
        <template #default="{ row }">{{ getPhasedValue(row, col) }}</template>
      </el-table-column>
      <el-table-column prop="owner" label="Owner" width="180" />
      <el-table-column v-if="colVisible.creator" prop="creator" label="Creator" width="180" />
      <el-table-column prop="status" label="Status" width="190" min-width="190">
        <template #default="{ row }">
          <el-select v-if="!snapshotMode && canEditStatusRow(row)" :model-value="row.status" size="small" style="width: 170px" @change="(val: string) => handleStatusChange(row, val)">
            <el-option v-for="s in allowedStatusRow(row)" :key="s" :value="s" :label="s" />
          </el-select>
          <el-tag v-else :type="statusType(row.status)" size="small">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="lastModified" label="Last Modified" width="155">
        <template #default="{ row }">{{ formatDate(row.lastModified) }}</template>
      </el-table-column>
      <el-table-column v-if="!isReadOnly || snapshotMode" label="Actions" width="140" align="center">
        <template #default="{ row }">
          <div v-if="!(row as any)._isChild" class="action-btns">
            <button class="action-icon" @click="$emit('history', row)" title="View History">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            </button>
            <button v-if="!snapshotMode && store.canCreate" class="action-icon" @click="$emit('duplicate', row)" title="Duplicate">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
            </button>
            <button v-if="!snapshotMode && canEditRow(row)" class="action-icon" @click="handleEditClick(row)" title="Edit">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            </button>
            <el-popconfirm v-if="!snapshotMode && canDeleteRow(row)" title="Delete all versions of this entry?" confirm-button-type="danger" @confirm="$emit('delete', row)">
              <template #reference>
                <button class="action-icon action-icon--danger" title="Delete">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>
                </button>
              </template>
            </el-popconfirm>
          </div>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { useEntryStore } from "@/stores/entryStore";
import { useLookupStore } from "@/stores/lookupStore";
import { entryApi } from "@/services/api";
import type { Entry } from "@/types";
import { STATUS_OPTIONS } from "@/types";
import { formatDate, formatMoney, formatVol } from "@/utils/formatters";
import { exportEntriesToExcel } from "@/utils/export";
import type { ExportColVisible, ExportPhasedCol } from "@/utils/export";

const props = withDefaults(
  defineProps<{
    entries: Entry[];
    isReadOnly?: boolean;
    snapshotMode?: boolean;
    canApprove?: boolean;
    exportFilename?: string;
  }>(),
  {
    isReadOnly: false,
    snapshotMode: false,
    canApprove: false,
    exportFilename: 'Export',
  }
);

const emit = defineEmits<{
  edit: [entry: Entry];
  duplicate: [entry: Entry];
  delete: [entry: Entry];
  history: [entry: Entry];
  approve: [entry: Entry];
  add: [];
}>();

const store = useEntryStore();
const lookupStore = useLookupStore();
const allFiltersOpen = ref(false);

// ── Snapshot-mode local filters (client-side, don't touch store) ──────────
const snapshotFilters = ref({
  division: "", country: "", categorisation: "", status: "",
  owner: "", ibpStep: "", channel: "", sub_channel: "", account: "",
  brand: "", brand_family: "",
});

function getFilter(key: keyof typeof snapshotFilters.value): string {
  if (props.snapshotMode) return snapshotFilters.value[key];
  return (store.filters as Record<string, string>)[key] ?? "";
}

function setFilter(key: keyof typeof snapshotFilters.value, value: string | undefined) {
  const val = value ?? "";
  if (props.snapshotMode) {
    snapshotFilters.value[key] = val;
  } else {
    (store.filters as Record<string, string>)[key] = val;
    store.fetchEntries();
  }
}

// Preload all top-level options on mount
onMounted(() => {
  lookupStore.preload();
  if (store.users.length === 0) store.fetchUsers();
});

// Quick filter state
const quickFilters = ref({
  openOnly: false,
  highPriority: false,
  recentlyModified: false,
});

const quickFilterDefs = [
  { key: "openOnly" as const, label: "Show Open Only" },
  { key: "highPriority" as const, label: "Show High Priority Only" },
  { key: "recentlyModified" as const, label: "Show Recently Modified Only" },
];

function toggleQuick(key: keyof typeof quickFilters.value) {
  quickFilters.value[key] = !quickFilters.value[key];
}

function toggleIbpStep(dept: string) {
  if (props.snapshotMode) {
    snapshotFilters.value.ibpStep = snapshotFilters.value.ibpStep === dept ? "" : dept;
  } else {
    store.filters.ibpStep = store.filters.ibpStep === dept ? "" : dept;
    store.fetchEntries();
  }
}

// ── Tree data (child impacts as inline rows) ──────────────────────────────
type TreeEntry = Entry & {
  _id: string;
  _isChild?: boolean;
  children?: TreeEntry[];
};

function toTreeRows(entries: Entry[]): TreeEntry[] {
  return entries.map((entry) => {
    const base: TreeEntry = { ...entry, _id: `e_${entry.id}` };
    if (!entry.childImpacts?.length) return base;
    return {
      ...base,
      children: entry.childImpacts.map((ci, idx) => ({
        ...entry,
        _id: `e_${entry.id}_c_${idx}`,
        _isChild: true,
        nsvAud: ci.nsvAud,
        nsvNzd: ci.nsvNzd,
        volumeLitres: ci.volumeLitres,
        impactPeriod: ci.impactPeriod,
        impactYear: ci.impactYear,
        childImpacts: [],
      })) as TreeEntry[],
    };
  });
}

// Client-side quick filter application
const filteredEntries = computed(() => {
  let result = props.entries;
  if (quickFilters.value.openOnly) {
    result = result.filter((e) => e.status === "Open");
  }
  if (quickFilters.value.highPriority) {
    result = result.filter((e) => e.probability === "High" || e.probability === "Very High");
  }
  if (quickFilters.value.recentlyModified) {
    const cutoff = Date.now() - 30 * 24 * 60 * 60 * 1000;
    result = result.filter((e) => e.lastModified && new Date(e.lastModified).getTime() > cutoff);
  }
  // Snapshot mode: all filtering is client-side
  if (props.snapshotMode) {
    const f = snapshotFilters.value;
    if (f.division) result = result.filter((e) => e.division === f.division);
    if (f.country) result = result.filter((e) => e.country === f.country);
    if (f.categorisation) result = result.filter((e) => e.categorisation === f.categorisation);
    if (f.status) result = result.filter((e) => e.status === f.status);
    if (f.owner) result = result.filter((e) => e.owner === f.owner);
    if (f.ibpStep) result = result.filter((e) => e.ibpStep === f.ibpStep);
    if (f.channel) result = result.filter((e) => e.channel === f.channel);
    if (f.sub_channel) result = result.filter((e) => e.subChannel === f.sub_channel);
    if (f.account) result = result.filter((e) => e.account === f.account);
    if (f.brand) result = result.filter((e) => e.brand === f.brand);
    if (f.brand_family) result = result.filter((e) => {
      const bf = e.brandFamily;
      return Array.isArray(bf) ? bf.includes(f.brand_family) : bf === f.brand_family;
    });
  }
  return result;
});

const treeData = computed(() => toTreeRows(filteredEntries.value));

// ── Lookup options from store (reactive, updates as cache fills) ──────────
const divisionOptions    = computed(() => lookupStore.getCached("division"));
const countryOptions     = computed(() => lookupStore.getCached("country"));
const channelOptions     = computed(() => lookupStore.getCached("channel"));
const categOptions       = computed(() => lookupStore.getCached("categorisation"));
const statusOptions      = computed(() => lookupStore.getCached("status"));
const ibpStepOptions     = computed(() => lookupStore.getCached("ibp_step"));

// Owner dropdown: users with role 0 (System Admin) or 1 (User)
const ownerOptions = computed(() =>
  store.users.filter((u) => u.role === 0 || u.role === 1)
);

// Cascade: Sub-Channel depends on Channel
const subChannelOptions = computed(() => {
  const ch = getFilter("channel");
  return ch ? lookupStore.getCached("sub_channel", ch) : lookupStore.getCached("sub_channel");
});
// Cascade: Account depends on Sub-Channel
const accountOptions = computed(() => {
  const sc = getFilter("sub_channel");
  return sc ? lookupStore.getCached("account", sc) : lookupStore.getCached("account");
});

// Brand standalone
const brandOptions = computed(() => lookupStore.getCached("brand"));

// Cascade: Brand Family depends on Brand
const brandFamilyOptions = computed(() => {
  const br = getFilter("brand");
  return br ? lookupStore.getCached("brand_family", br) : lookupStore.getCached("brand_family");
});

// Main-mode cascade watches (skip in snapshot mode)
watch(() => store.filters.channel, (val) => {
  if (props.snapshotMode) return;
  store.filters.sub_channel = "";
  store.filters.account = "";
  if (val) lookupStore.loadChildren("sub_channel", val);
  store.fetchEntries();
});
watch(() => store.filters.sub_channel, (val) => {
  if (props.snapshotMode) return;
  store.filters.account = "";
  if (val) lookupStore.loadChildren("account", val);
  store.fetchEntries();
});
watch(() => store.filters.brand, (val) => {
  if (props.snapshotMode) return;
  store.filters.brand_family = "";
  if (val) lookupStore.loadChildren("brand_family", val);
  store.fetchEntries();
});

// Snapshot-mode cascade watches
watch(() => snapshotFilters.value.channel, (val) => {
  if (!props.snapshotMode) return;
  snapshotFilters.value.sub_channel = "";
  snapshotFilters.value.account = "";
  if (val) lookupStore.loadChildren("sub_channel", val);
});
watch(() => snapshotFilters.value.sub_channel, (val) => {
  if (!props.snapshotMode) return;
  snapshotFilters.value.account = "";
  if (val) lookupStore.loadChildren("account", val);
});
watch(() => snapshotFilters.value.brand, (val) => {
  if (!props.snapshotMode) return;
  snapshotFilters.value.brand_family = "";
  if (val) lookupStore.loadChildren("brand_family", val);
});

// ── Header/body column width sync (body: auto layout → read actual widths → write to header colgroup) ──
const tableWrapper = ref<HTMLElement>();

function _syncOneTable(elTable: Element) {
  const bodyTable   = elTable.querySelector('.el-table__body-wrapper table') as HTMLTableElement | null;
  const headerTable = elTable.querySelector('.el-table__header-wrapper table') as HTMLTableElement | null;
  if (!bodyTable || !headerTable) return;

  const ths      = headerTable.querySelectorAll('thead th');
  const firstRow = bodyTable.querySelector('tbody tr:first-child');
  const tds      = firstRow ? firstRow.querySelectorAll('td') : ([] as unknown as NodeListOf<Element>);
  const hCols    = headerTable.querySelectorAll('colgroup col');
  const bCols    = bodyTable.querySelectorAll('colgroup col');

  const n = Math.max(ths.length, tds.length);
  let total = 0;
  for (let i = 0; i < n; i++) {
    const hw = (ths[i] as HTMLElement | undefined)?.offsetWidth ?? 0;
    const bw = (tds[i] as HTMLElement | undefined)?.offsetWidth ?? 0;
    const w  = Math.max(hw, bw);
    total += w;
    if (hCols[i]) (hCols[i] as HTMLElement).style.cssText = `width:${w}px;min-width:${w}px;`;
    if (bCols[i]) (bCols[i] as HTMLElement).style.cssText = `width:${w}px;min-width:${w}px;`;
  }
  headerTable.style.width = bodyTable.style.width = total + 'px';
}

function syncAllHeaders() {
  tableWrapper.value?.querySelectorAll('.el-table').forEach(_syncOneTable);
}

watch(filteredEntries, () => {
  nextTick(() => requestAnimationFrame(syncAllHeaders));
}, { immediate: true });

// ── Split view ────────────────────────────────────────────────────────────
const splitByOptions = [
  { key: "country",     label: "Country" },
  { key: "division",    label: "Division" },
  { key: "ibpStep",  label: "IBP Step" },
  { key: "rAndO",       label: "Risk vs. Opportunity" },
  { key: "probability", label: "Priority" },
];

const splitBy = ref<string[]>([]);
watch(splitBy, () => { nextTick(() => requestAnimationFrame(syncAllHeaders)); });

const groupedEntries = computed(() => {
  const dims = splitBy.value;
  if (!dims.length) return [];

  const groupMap = new Map<string, { entries: Entry[]; vals: string[] }>();
  for (const row of filteredEntries.value) {
    const vals = dims.map(d => (row as unknown as Record<string, unknown>)[d] as string || "—");
    const key = vals.join("\0");
    if (!groupMap.has(key)) groupMap.set(key, { entries: [], vals });
    groupMap.get(key)!.entries.push(row);
  }

  return Array.from(groupMap.values())
    .sort((a, b) => a.vals.join("").localeCompare(b.vals.join("")))
    .map(({ entries, vals }) => ({
      key: vals.join(" | "),
      breadcrumb: dims.map((d, i) => ({
        label: splitByOptions.find(o => o.key === d)?.label ?? d,
        val: vals[i],
      })),
      entries,
    }));
});

const colVisible = ref({
  ibpStep: true,
  subChannel: true,
  account: true,
  brandFamily: true,
  description: true,
  nsvAud: true,
  nsvNzd: true,
  volumeLitres: true,
  impactPeriod: true,
  creator: true,
});

function rowClassName({ row }: { row: Entry }) {
  if ((row as TreeEntry)._isChild) return "child-impact-row";
  const classes: string[] = [];
  const statusMap: Record<string, string> = {
    "Approved":             "row-approved",
    "Dismissed":            "row-dismissed",
    "Included in Forecast": "row-forecast",
  };
  if (statusMap[row.status ?? ""]) classes.push(statusMap[row.status ?? ""]);
  return classes.join(" ");
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

function canEditRow(row: Entry): boolean {
  if ((row as TreeEntry)._isChild) return false;
  const role = store.userRole;
  if (role === "System Admin") return true;
  if (role === "User") return row.status === "Open";
  return store.canCreate;
}

async function handleEditClick(row: Entry) {
  if ((row as TreeEntry)._isChild) return;
  try {
    const { status } = await entryApi.getStatus(row.id);
    if (status !== "Open") {
      ElMessage.warning(`This entry is now "${status}" and can no longer be edited.`);
      await store.fetchEntries();
      return;
    }
  } catch {
    ElMessage.error("Unable to verify entry status. Please refresh and try again.");
    await store.fetchEntries();
    return;
  }
  emit("edit", row);
}

function canDeleteRow(row: Entry): boolean {
  if ((row as TreeEntry)._isChild) return false;
  const role = store.userRole;
  if (role === "System Admin") return true;
  if (role === "User") return row.status === "Open";
  return false;
}

function canEditStatusRow(row: Entry): boolean {
  if ((row as TreeEntry)._isChild) return false;
  const role = store.userRole;
  const status = row.status;
  if (role === "System Admin") return true;
  if (role === "Department Approver") return status === "Open" || status === "Approved";
  if (role === "Finance Approver") return status === "Approved" || status === "Dismissed" || status === "Included in Forecast";
  return false;
}

function allowedStatusRow(row: Entry): string[] {
  const role = store.userRole;
  const status = row.status ?? "Open";
  if (role === "System Admin") return STATUS_OPTIONS;
  if (role === "Department Approver" && (status === "Open" || status === "Approved")) return ["Open", "Approved"];
  if (role === "Finance Approver") return ["Approved", "Dismissed", "Included in Forecast"];
  return [status];
}

async function handleStatusChange(row: Entry, newStatus: string) {
  try {
    const { status: latestStatus } = await entryApi.getStatus(row.id);
    if (latestStatus !== row.status) {
      ElMessage.warning(`This entry's status has changed to "${latestStatus}". Please review the latest state.`);
      await store.fetchEntries();
      return;
    }
    await entryApi.updateStatus(row.id, newStatus, store.currentUser?.email);
    await store.fetchEntries();
    ElMessage.success("Status updated");
  } catch {
    ElMessage.error("Unable to verify entry status. Please refresh and try again.");
    await store.fetchEntries();
  }
}

function sumChildField(row: Entry, field: "nsvAud" | "nsvNzd" | "volumeLitres"): string | undefined {
  if (!row.childImpacts?.length) return row[field];
  const total = row.childImpacts.reduce((acc, ci) => {
    const v = parseFloat(ci[field] ?? "");
    return acc + (isNaN(v) ? 0 : v);
  }, 0);
  return total === 0 ? undefined : String(total);
}

function formatNsvImpact(row: Entry) {
  if (row.country === "New Zealand") return formatMoney(sumChildField(row, "nsvNzd"));
  return formatMoney(sumChildField(row, "nsvAud"));
}


function countryAbbr(country?: string): string {
  if (!country) return "—";
  const map: Record<string, string> = {
    "Australia": "AU",
    "New Zealand": "NZ",
  };
  return map[country] ?? country;
}

function formatImpactPeriod(row: Entry): string {
  const children = (row as TreeEntry)._isChild ? [] : (row.childImpacts ?? []);

  if (!children.length) {
    if (row.impactPeriod && row.impactYear) return `${row.impactPeriod} ${row.impactYear}`;
    return row.impactPeriod || row.impactYear || "—";
  }

  const parsed = children
    .map((c) => ({
      period: c.impactPeriod ?? "",
      year: c.impactYear ?? "",
      num: parseInt((c.impactPeriod ?? "").replace("F", "")) || 0,
      yearNum: parseInt(c.impactYear ?? "") || 0,
    }))
    .filter((c) => c.num > 0 && c.yearNum > 0)
    .sort((a, b) => a.yearNum !== b.yearNum ? a.yearNum - b.yearNum : a.num - b.num);

  if (!parsed.length) return "—";

  // Group consecutive periods (same year +1, or F12→F01 next year)
  const groups: (typeof parsed)[] = [];
  let cur = [parsed[0]];
  for (let i = 1; i < parsed.length; i++) {
    const prev = cur[cur.length - 1];
    const c = parsed[i];
    const consecutive =
      (c.yearNum === prev.yearNum && c.num === prev.num + 1) ||
      (c.yearNum === prev.yearNum + 1 && prev.num === 12 && c.num === 1);
    if (consecutive) cur.push(c);
    else { groups.push(cur); cur = [c]; }
  }
  groups.push(cur);

  return groups
    .map((g) =>
      g.length === 1
        ? `${g[0].period} ${g[0].year}`
        : `${g[0].period} ${g[0].year} - ${g[g.length - 1].period} ${g[g.length - 1].year}`
    )
    .join(", ");
}

function divisionEmoji(division?: string): string {
  if (!division) return "";
  const d = division.toLowerCase();
  if (d.includes("alcohol") && !d.includes("non-alcohol")) return "🍷";
  return "💧";
}

function clearFilters() {
  quickFilters.value = { openOnly: false, highPriority: false, recentlyModified: false };
  if (props.snapshotMode) {
    Object.keys(snapshotFilters.value).forEach((k) => {
      (snapshotFilters.value as Record<string, string>)[k] = "";
    });
  } else {
    store.resetFilters();
    store.fetchEntries();
  }
}

// ── Period Phased View ────────────────────────────────────────────────────
type PhasedView = "none" | "month" | "quarter" | "half" | "year";

interface PhasedCol {
  key: string;
  label: string;
  year: string;
  periods: string[];
  width: number;
}

const MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

const phasedView = ref<PhasedView>("none");

const displayYears = computed(() => {
  const y = new Date().getFullYear();
  return [String(y), String(y + 1)];
});

const phasedColumns = computed((): PhasedCol[] => {
  if (phasedView.value === "none") return [];
  const cols: PhasedCol[] = [];
  for (const year of displayYears.value) {
    if (phasedView.value === "month") {
      for (let i = 0; i < 12; i++) {
        const period = `F${String(i + 1).padStart(2, "0")}`;
        cols.push({ key: `${year}-${period}`, label: `${MONTH_NAMES[i]} '${year.slice(2)}`, year, periods: [period], width: 88 });
      }
    } else if (phasedView.value === "quarter") {
      const qs = [
        { suffix: "Q1", periods: ["F01","F02","F03"] },
        { suffix: "Q2", periods: ["F04","F05","F06"] },
        { suffix: "Q3", periods: ["F07","F08","F09"] },
        { suffix: "Q4", periods: ["F10","F11","F12"] },
      ];
      for (const q of qs) {
        cols.push({ key: `${year}-${q.suffix}`, label: `${q.suffix} ${year}`, year, periods: q.periods, width: 105 });
      }
    } else if (phasedView.value === "half") {
      cols.push({ key: `${year}-H1`, label: `H1 ${year}`, year, periods: ["F01","F02","F03","F04","F05","F06"], width: 115 });
      cols.push({ key: `${year}-H2`, label: `H2 ${year}`, year, periods: ["F07","F08","F09","F10","F11","F12"], width: 115 });
    } else {
      cols.push({ key: year, label: year, year, periods: ["F01","F02","F03","F04","F05","F06","F07","F08","F09","F10","F11","F12"], width: 120 });
    }
  }
  return cols;
});
watch(phasedColumns, () => { nextTick(() => requestAnimationFrame(syncAllHeaders)); });

function getPhasedValue(row: Entry, col: PhasedCol): string {
  const r = row as TreeEntry;
  const field = row.country === "New Zealand" ? "nsvNzd" : "nsvAud";
  // Child row: check only this row's own period
  if (r._isChild) {
    if (String(row.impactYear) === col.year && col.periods.includes(row.impactPeriod ?? "")) {
      const v = parseFloat((row[field] as string) ?? "");
      return isNaN(v) || v === 0 ? "-" : formatMoney(String(v));
    }
    return "-";
  }
  // Parent row: sum all child impacts
  if (!row.childImpacts?.length) return "-";
  const total = row.childImpacts.reduce((acc, ci) => {
    if (String(ci.impactYear) === col.year && col.periods.includes(ci.impactPeriod ?? "")) {
      const v = parseFloat((ci[field] as string) ?? "");
      return acc + (isNaN(v) ? 0 : v);
    }
    return acc;
  }, 0);
  return total === 0 ? "-" : formatMoney(String(total));
}

function handleExport(entriesToExport: Entry[], label?: string) {
  const safe = label ? label.replace(/[\s|\\/:*?"<>]/g, '_') : '';
  const fname = safe ? `${props.exportFilename}_${safe}` : props.exportFilename;
  exportEntriesToExcel(
    entriesToExport,
    colVisible.value as unknown as ExportColVisible,
    phasedColumns.value as unknown as ExportPhasedCol[],
    fname,
  );
}
</script>

<style scoped>
.entries-table-wrapper {
  background: var(--bg-primary);
  border-radius: var(--radius);
  border: 1px solid var(--border-color);
  overflow: hidden;
  box-shadow: var(--shadow);
}

/* ── Quick Filters ── */
.quick-filters-section {
  padding: 16px 24px 12px;
  border-bottom: 1px solid var(--border-color);
}

.section-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  margin: 0 0 10px;
}

.quick-filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}
.quick-filter-row:last-child {
  margin-bottom: 0;
}

.quick-btn {
  display: inline-flex;
  align-items: center;
  padding: 5px 14px;
  border-radius: 6px;
  border: 1px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
  line-height: 1.4;
}
.quick-btn:hover {
  border-color: #6b7280;
  background: #f5f7fa;
}
.quick-btn.active {
  border-color: var(--primary, #030213);
  background: var(--primary, #030213);
  color: #fff;
}

/* ── All Filters ── */
.all-filters-section {
  border-bottom: 1px solid var(--border-color);
}

.all-filters-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 12px 24px;
  cursor: pointer;
  user-select: none;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}
.all-filters-header:hover {
  background: #f9fafb;
}

.chevron-icon {
  width: 16px;
  height: 16px;
  color: var(--text-secondary);
  transition: transform 0.2s;
  flex-shrink: 0;
}
.chevron-icon.open {
  transform: rotate(180deg);
}

.all-filters-body {
  padding: 4px 24px 16px;
}

.filter-row {
  margin-bottom: 12px;
}

.filter-label {
  display: block;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.filter-group-label {
  font-size: 12px;
  font-weight: 600;
  color: #8b5cf6;
  margin: 4px 0 10px;
}

:deep(.all-filters-body .el-select),
:deep(.all-filters-body .el-input) {
  width: 100%;
}

.filter-actions {
  margin-top: 4px;
  display: flex;
  justify-content: flex-end;
}

/* ── Table Toolbar ── */
.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid var(--border-color);
  background: linear-gradient(180deg, rgba(245, 247, 251, 0.8) 0%, rgba(241, 245, 252, 0.9) 100%);
}

.entry-count {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

.toolbar-right {
  display: flex;
  gap: 8px;
  align-items: center;
}

.column-selector {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.column-selector-title {
  font-weight: 600;
  margin: 0 0 8px;
  color: var(--text-primary);
}

/* ── Tree toggle column ── */
:deep(.tree-toggle-col) {
  padding: 0 !important;
}
:deep(.tree-toggle-col .cell) {
  padding: 0 4px !important;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ── Phased View control ── */
.phased-view-control {
  display: flex;
  align-items: center;
  gap: 6px;
}

.phased-view-label {
  font-size: 13px;
  color: var(--text-secondary);
  white-space: nowrap;
}

:deep(.phased-col) {
  background-color: #f0f7ff !important;
}
:deep(.phased-col .cell) {
  font-variant-numeric: tabular-nums;
  font-size: 13px;
}

/* ── Expand / Child Impacts ── */
.child-impacts {
  padding: 16px 24px;
}

.child-impacts-title {
  font-weight: 600;
  margin: 0 0 8px;
  color: var(--text-primary);
}

:deep(.row-approved) td {
  background-color: #f0fdf4 !important;
}
:deep(.row-dismissed) td {
  background-color: #f3f4f6 !important;
}
:deep(.row-forecast) td {
  background-color: #eff6ff !important;
}
:deep(.no-expand .el-table__expand-icon) {
  visibility: hidden;
  pointer-events: none;
}
:deep(.child-impact-row) td {
  background-color: #fafbfd !important;
  color: var(--text-secondary) !important;
  font-size: 12.5px;
}
:deep(.child-impact-row) td .cell {
  opacity: 0.85;
}


/* ── Action Buttons ── */
.action-btns {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.action-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  border-radius: 6px;
  cursor: pointer;
  color: #6b7280;
  transition: background 0.15s, color 0.15s;
  padding: 0;
}

.action-icon svg {
  width: 15px;
  height: 15px;
}

.action-icon:hover {
  background: #f3f4f6;
  color: #111827;
}

.action-icon--danger {
  color: #d4183d;
}

.action-icon--danger:hover {
  background: #fff1f3;
  color: #d4183d;
}

/* ── Table header: never truncate ── */
:deep(.el-table th .cell) {
  white-space: nowrap;
  overflow: visible;
  text-overflow: clip;
}

/* ── Both header and body expand to fit content; JS syncs them by taking the max width of each column ── */
:deep(.el-table__header-wrapper table),
:deep(.el-table__body-wrapper table) {
  table-layout: auto !important;
  width: auto !important;
}
:deep(.el-table td .cell) {
  white-space: nowrap;
}
/* Force el-select to fill the table cell so inline-flex doesn't collapse it to zero width */
:deep(.el-table td .cell .el-select) {
  display: block;
  width: 100%;
}
:deep(.el-table td .cell .el-select .el-select__wrapper) {
  width: 100%;
  box-sizing: border-box;
}

/* ── Table horizontal scrollbar ── */
:deep(.el-table__body-wrapper .el-scrollbar__bar.is-horizontal) {
  height: 8px;
  bottom: 0;
  opacity: 1 !important;
}
:deep(.el-table__body-wrapper .el-scrollbar__thumb) {
  background-color: rgba(0, 0, 0, 0.22);
  border-radius: 4px;
  transition: background-color 0.2s;
}
:deep(.el-table__body-wrapper .el-scrollbar__thumb:hover) {
  background-color: rgba(0, 0, 0, 0.42);
}
:deep(.el-table__body-wrapper .el-scrollbar__wrap) {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

/* ── Probability Badge ── */
.prob-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
  cursor: default;
}
.prob-high    { background: #0d9488; color: #fff; }
.prob-medium  { background: #cffafe; color: #0e7490; }
.prob-low     { background: #e0f2fe; color: #0369a1; }

/* ── Split Group ── */
.split-group {
  margin-bottom: 24px;
}

.split-group-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: #f8f9fc;
  border-left: 3px solid #030213;
  border-top: 1px solid var(--border-color);
  border-bottom: 1px solid var(--border-color);
}

.split-group-breadcrumb {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}

.split-sep {
  color: #9ca3af;
  font-size: 13px;
  padding: 0 2px;
  line-height: 1;
}

.split-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 3px 9px;
  font-size: 12px;
}

.split-chip-label {
  color: #9ca3af;
  font-weight: 500;
}

.split-chip-val {
  color: #111827;
  font-weight: 600;
}

.split-header-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.split-count {
  font-size: 12px;
  font-weight: 600;
  color: #fff;
  background: #030213;
  border-radius: 20px;
  padding: 2px 12px;
  white-space: nowrap;
}
</style>
