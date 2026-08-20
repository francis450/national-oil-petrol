<template>
	<div class="space-y-4">
		<!-- Header with Search and Actions -->
		<div class="flex flex-col sm:flex-row gap-4 items-center justify-between">
			<div class="flex gap-2 flex-1">
				<!-- Search Input -->
				<Input
					v-model="searchQuery"
					placeholder="Search..."
					class="flex-1"
					@update:modelValue="debounceSearch"
				/>

				<!-- Refresh Button -->
				<Button
					variant="secondary"
					@click="$emit('refresh')"
					title="Refresh"
					class="flex-shrink-0"
				>
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
						/>
					</svg>
				</Button>
			</div>

			<!-- Action Buttons -->
			<div class="flex gap-2 flex-shrink-0">
				<Button v-if="showExport" variant="secondary" @click="$emit('export')">
					<svg
						class="w-4 h-4 mr-1"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
						/>
					</svg>
					Export
				</Button>

				<Button v-if="showAdd" variant="primary" @click="$emit('add')">
					<svg
						class="w-4 h-4 mr-1"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 6v6m0 0v6m0-6h6m-6 0H6"
						/>
					</svg>
					{{ addLabel }}
				</Button>
			</div>
		</div>

		<!-- Loading State -->
		<Card v-if="loading" class="text-center py-12">
			<div class="flex items-center justify-center gap-4">
				<div
					class="animate-spin rounded-full h-8 w-8 border-4 border-primary-500 border-t-transparent"
				/>
				<span class="text-gray-400">Loading...</span>
			</div>
		</Card>

		<!-- Error State -->
		<Card v-else-if="error" class="p-4 border border-danger-500 bg-danger-600/10">
			<div class="flex items-center gap-3 text-danger-500">
				<svg
					class="w-5 h-5 flex-shrink-0"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
					/>
				</svg>
				<span class="text-sm">{{ error }}</span>
			</div>
		</Card>

		<!-- Empty State -->
		<Card v-else-if="!loading && filteredData.length === 0" class="text-center py-12">
			<div class="flex flex-col items-center gap-4">
				<svg
					class="w-12 h-12 text-gray-500"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
					/>
				</svg>
				<p class="text-gray-400">No {{ title?.toLowerCase() || "data" }} found</p>
				<p v-if="searchQuery" class="text-sm text-gray-500">Try adjusting your search</p>
				<Button
					v-if="showAdd && searchQuery"
					variant="primary"
					@click="clearSearch"
					class="mt-2"
				>
					Clear Search
				</Button>
			</div>
		</Card>

		<!-- Data Table -->
		<div v-else class="overflow-x-auto rounded-xl border border-border">
			<table class="w-full text-sm">
				<thead class="bg-surface-elevated border-b border-border">
					<tr>
						<th
							v-for="col in columns"
							:key="col.key"
							:class="[
								'px-4 py-3 text-left text-gray-400 font-medium',
								'text-xs uppercase tracking-wider',
								{ 'cursor-pointer select-none': col.sortable },
								{ 'bg-surface-elevated/50': sortColumn === col.key },
							]"
							@click="sortBy(col.key)"
						>
							<div class="flex items-center gap-1">
								<span>{{ col.label }}</span>
								<div v-if="col.sortable" class="flex flex-col">
									<svg
										class="w-3 h-3 transition-colors"
										:class="{
											'text-primary-500':
												sortColumn === col.key && sortDirection === 'asc',
											'text-gray-600': !(
												sortColumn === col.key && sortDirection === 'asc'
											),
										}"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M5 15l7-7 7 7"
										/>
									</svg>
									<svg
										class="w-3 h-3 transition-colors"
										:class="{
											'text-primary-500':
												sortColumn === col.key && sortDirection === 'desc',
											'text-gray-600': !(
												sortColumn === col.key && sortDirection === 'desc'
											),
										}"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M19 9l-7 7-7-7"
										/>
									</svg>
								</div>
							</div>
						</th>
						<th
							v-if="showActions"
							class="px-4 py-3 text-center text-gray-400 font-medium text-xs uppercase tracking-wider"
						>
							Actions
						</th>
					</tr>
				</thead>
				<tbody>
					<tr
						v-for="(row, idx) in paginatedData"
						:key="idx"
						:class="[
							'border-b border-border',
							'hover:bg-surface-elevated/50 transition-colors',
							{ 'bg-surface-elevated/30': selectedRow === idx },
						]"
						@click="selectRow(idx)"
					>
						<td v-for="col in columns" :key="col.key" class="px-4 py-3 text-gray-300">
							<slot :name="`cell-${col.key}`" :data="row">
								{{ formatCellValue(row[col.key], col.type) }}
							</slot>
						</td>
						<td
							v-if="showActions"
							class="px-4 py-3 text-center space-x-2 flex justify-center"
						>
							<Button
								v-if="showEdit"
								variant="ghost"
								size="sm"
								@click.stop="$emit('edit', row)"
							>
								Edit
							</Button>
							<Button
								v-if="showDelete"
								variant="ghost"
								size="sm"
								class="text-danger-400 hover:text-danger-300"
								@click.stop="$emit('delete', row)"
							>
								Delete
							</Button>
						</td>
					</tr>
				</tbody>
			</table>
		</div>

		<!-- Pagination -->
		<div
			v-if="!loading && filteredData.length > 0 && showPagination"
			class="flex flex-col sm:flex-row items-center justify-between gap-4"
		>
			<div class="flex items-center gap-4">
				<!-- Items per page selector -->
				<Select
					v-model="itemsPerPage"
					:options="pageSizeOptions"
					class="w-20"
					@update:modelValue="resetPagination"
				/>

				<!-- Pagination info -->
				<p class="text-sm text-gray-400">
					Showing {{ paginationStart }} - {{ paginationEnd }} of
					{{ data.length }} records
				</p>
			</div>

			<div class="flex gap-2">
				<Button variant="secondary" :disabled="currentPage === 1" @click="prevPage">
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M15 19l-7-7 7-7"
						/>
					</svg>
				</Button>

				<span class="px-4 py-2 bg-surface-elevated rounded-xl text-sm text-gray-300">
					Page {{ currentPage }} of {{ totalPages }}
				</span>

				<Button
					variant="secondary"
					:disabled="currentPage === totalPages"
					@click="nextPage"
				>
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M9 5l7 7-7 7"
						/>
					</svg>
				</Button>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import Card from "@/components/ui/Card.vue";
import Button from "@/components/ui/Button.vue";
import Input from "@/components/ui/Input.vue";
import Select from "@/components/ui/Select.vue";

interface Column {
	key: string;
	label: string;
	type?: "text" | "number" | "currency" | "date" | "status" | "boolean";
	sortable?: boolean;
}

const props = withDefaults(
	defineProps<{
		title?: string;
		columns: Column[];
		data: any[];
		loading?: boolean;
		error?: string;
		showAdd?: boolean;
		showEdit?: boolean;
		showDelete?: boolean;
		showActions?: boolean;
		showExport?: boolean;
		showPagination?: boolean;
		addLabel?: string;
		itemsPerPage?: number;
		selectable?: boolean;
	}>(),
	{
		loading: false,
		error: "",
		showAdd: true,
		showEdit: true,
		showDelete: false,
		showActions: true,
		showExport: false,
		showPagination: true,
		addLabel: "New",
		itemsPerPage: 10,
		selectable: false,
	}
);

const emit = defineEmits<{
	add: [];
	edit: [data: any];
	delete: [data: any];
	refresh: [];
	export: [];
	"row-click": [data: any, index: number];
	sort: [column: string, direction: "asc" | "desc"];
}>();

// Search and filtering
const searchQuery = ref("");
const searchTimeout = ref<ReturnType<typeof setTimeout> | null>(null);

const debounceSearch = () => {
	if (searchTimeout.value) {
		clearTimeout(searchTimeout.value);
	}
	searchTimeout.value = setTimeout(() => {
		// Search is handled by computed filteredData
	}, 300);
};

const clearSearch = () => {
	searchQuery.value = "";
};

// Sorting
const sortColumn = ref<string | null>(null);
const sortDirection = ref<"asc" | "desc">("asc");

const sortBy = (column: string) => {
	const col = props.columns.find((c) => c.key === column);
	if (!col || !col.sortable) return;

	if (sortColumn.value === column) {
		sortDirection.value = sortDirection.value === "asc" ? "desc" : "asc";
	} else {
		sortColumn.value = column;
		sortDirection.value = "asc";
	}

	emit("sort", column, sortDirection.value);
};

// Pagination
const currentPage = ref(1);
const pageSizeOptions = [
	{ value: 5, label: "5" },
	{ value: 10, label: "10" },
	{ value: 25, label: "25" },
	{ value: 50, label: "50" },
	{ value: 100, label: "100" },
];

const resetPagination = () => {
	currentPage.value = 1;
};

const prevPage = () => {
	if (currentPage.value > 1) {
		currentPage.value--;
	}
};

const nextPage = () => {
	if (currentPage.value < totalPages.value) {
		currentPage.value++;
	}
};

// Row selection
const selectedRow = ref<number | null>(null);

const selectRow = (index: number) => {
	if (!props.selectable) return;
	selectedRow.value = selectedRow.value === index ? null : index;
	emit("row-click", paginatedData.value[index], index);
};

// Computed properties
const filteredData = computed(() => {
	let result = [...props.data];

	// Apply search filter
	if (searchQuery.value) {
		const query = searchQuery.value.toLowerCase();
		result = result.filter((row) =>
			Object.values(row).some((val) => String(val).toLowerCase().includes(query))
		);
	}

	// Apply sorting
	if (sortColumn.value) {
		const column = props.columns.find((c) => c.key === sortColumn.value);
		if (column) {
			result.sort((a, b) => {
				const aVal = a[column.key];
				const bVal = b[column.key];

				if (aVal === bVal) return 0;
				if (aVal === null || aVal === undefined) return 1;
				if (bVal === null || bVal === undefined) return -1;

				const aStr = String(aVal);
				const bStr = String(bVal);

				if (sortDirection.value === "asc") {
					return aStr.localeCompare(bStr);
				} else {
					return bStr.localeCompare(aStr);
				}
			});
		}
	}

	return result;
});

const totalPages = computed(() => {
	return Math.ceil(filteredData.value.length / props.itemsPerPage);
});

const paginatedData = computed(() => {
	const start = (currentPage.value - 1) * props.itemsPerPage;
	const end = start + props.itemsPerPage;
	return filteredData.value.slice(start, end);
});

const paginationStart = computed(() => {
	return filteredData.value.length === 0 ? 0 : (currentPage.value - 1) * props.itemsPerPage + 1;
});

const paginationEnd = computed(() => {
	return Math.min(currentPage.value * props.itemsPerPage, filteredData.value.length);
});

// Format cell values
const formatCellValue = (value: any, type?: string): string => {
	if (value === null || value === undefined) return "—";

	switch (type) {
		case "currency":
			return `KSh ${Number(value).toLocaleString()}`;
		case "number":
			return Number(value).toLocaleString();
		case "date":
			return new Date(value).toLocaleDateString("en-KE", {
				year: "numeric",
				month: "short",
				day: "numeric",
			});
		case "status":
			return String(value).charAt(0).toUpperCase() + String(value).slice(1);
		case "boolean":
			return value ? "Yes" : "No";
		default:
			return String(value);
	}
};

// Watch for data changes
watch(
	() => props.data,
	() => {
		resetPagination();
	},
	{ deep: true }
);
</script>

<style scoped></style>
