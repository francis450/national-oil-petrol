<template>
	<header
		class="bg-surface-elevated border-b border-border px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center sticky top-0 z-30"
	>
		<!-- Left: Sidebar Toggle & Breadcrumb -->
		<div class="flex items-center gap-4">
			<!-- Mobile Sidebar Toggle -->
			<button
				@click="$emit('menu-click')"
				class="lg:hidden text-gray-400 hover:text-primary-400 transition-colors p-2 hover:bg-surface rounded-xl"
				:title="uiStore.sidebarOpen ? 'Hide sidebar' : 'Show sidebar'"
			>
				<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M4 6h16M4 12h16M4 18h16"
					/>
				</svg>
			</button>

			<!-- Breadcrumb or Page Title -->
			<div class="text-gray-400 text-sm hidden md:block">
				<span v-if="pageTitle" class="text-white font-medium">{{ pageTitle }}</span>
			</div>
		</div>

		<!-- Right: Actions -->
		<div class="flex items-center gap-2 sm:gap-4">
			<!-- Last Updated -->
			<div class="text-xs text-gray-500 hidden sm:block">
				<span v-if="lastUpdated">Updated {{ lastUpdated }}</span>
			</div>

			<!-- Dark Mode Toggle -->
			<button
				@click="uiStore.toggleDarkMode"
				class="text-gray-400 hover:text-yellow-400 transition-colors p-2 hover:bg-surface rounded-xl"
				:title="uiStore.darkMode ? 'Light mode' : 'Dark mode'"
			>
				<svg
					v-if="uiStore.darkMode"
					class="w-5 h-5"
					fill="currentColor"
					viewBox="0 0 20 20"
				>
					<path
						fill-rule="evenodd"
						d="M17.293 13.293a8 8 0 01-11.586 0L5.5 11.5a.5.5 0 00-.707.707l.086.086a9 9 0 0012.728 0l.086-.086a.5.5 0 00-.707-.707l-.707.707zM10 15a.5.5 0 01.5-.5h5a.5.5 0 010 1h-5a.5.5 0 01-.5-.5zm0-5a.5.5 0 01.5-.5h5a.5.5 0 010 1h-5a.5.5 0 01-.5-.5z"
						clip-rule="evenodd"
					/>
				</svg>
				<svg v-else class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
					<path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
				</svg>
			</button>

			<!-- User Menu -->
			<div class="relative">
				<button
					@click="showUserMenu = !showUserMenu"
					class="flex items-center gap-2 px-3 py-2 rounded-xl text-gray-300 hover:bg-surface transition-colors"
				>
					<div
						class="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center text-sm font-bold"
					>
						{{ userInitial }}
					</div>
					<span class="hidden sm:block text-sm">{{ userName }}</span>
					<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
						<path
							fill-rule="evenodd"
							d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
							clip-rule="evenodd"
						/>
					</svg>
				</button>

				<!-- Dropdown Menu -->
				<transition
					enter-active-class="transition duration-100 ease-out"
					enter-from-class="transform opacity-0 scale-95"
					enter-to-class="transform opacity-100 scale-100"
					leave-active-class="transition duration-75 ease-in"
					leave-from-class="transform opacity-100 scale-100"
					leave-to-class="transform opacity-0 scale-95"
				>
					<div
						v-if="showUserMenu"
						class="absolute right-0 mt-2 w-48 bg-surface-elevated rounded-xl shadow-lg border border-border z-50"
					>
						<div class="px-4 py-3 border-b border-border">
							<p class="text-sm font-medium text-white">{{ userName }}</p>
							<p class="text-xs text-gray-400">{{ userEmail }}</p>
						</div>
						<div class="py-2">
							<button
								@click="viewProfile"
								class="w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-surface hover:text-primary-400 transition-colors"
							>
								Profile Settings
							</button>
							<button
								@click="logout"
								class="w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-surface hover:text-danger-400 transition-colors"
							>
								Logout
							</button>
						</div>
					</div>
				</transition>
			</div>
		</div>
	</header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { useUIStore } from "@/stores/ui";

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const uiStore = useUIStore();

const showUserMenu = ref(false);

const userName = computed(() => authStore.user?.full_name || "User");
const userEmail = computed(() => authStore.user?.email || "");
const userInitial = computed(() => {
	const name = userName.value;
	return name.charAt(0).toUpperCase();
});

const pageTitle = computed(() => {
	// Map routes to readable titles
	const routePath = route.path;
	const titles: Record<string, string> = {
		"/": "Dashboard",
		"/fuel": "Fuel Operations",
		"/sales": "Sales",
		"/receivables": "Receivables",
		"/payables": "Payables",
		"/inventory": "Inventory",
		"/finance": "Finance",
		"/hr": "Human Resources",
		"/reports": "Reports",
	};

	for (const [path, title] of Object.entries(titles)) {
		if (routePath === path || routePath.startsWith(path + "/")) {
			return title;
		}
	}
	return "National Oil";
});

const lastUpdated = computed(() => {
	const now = new Date();
	const hours = now.getHours();
	const minutes = now.getMinutes();
	return `at ${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}`;
});

const logout = async () => {
	await authStore.logout();
	router.push("/login");
};

const viewProfile = () => {
	// TODO: Implement profile settings
	showUserMenu.value = false;
};

// Close user menu when clicking outside
const handleClickOutside = (event: MouseEvent) => {
	const target = event.target as HTMLElement;
	if (!target.closest(".relative") && showUserMenu.value) {
		showUserMenu.value = false;
	}
};

onMounted(() => {
	document.addEventListener("click", handleClickOutside);
});

onUnmounted(() => {
	document.removeEventListener("click", handleClickOutside);
});

defineEmits(["menu-click"]);
</script>

<style scoped></style>
