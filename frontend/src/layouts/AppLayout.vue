<template>
	<div class="flex h-screen bg-surface">
		<!-- Mobile Sidebar Overlay -->
		<transition
			enter-active-class="transition-opacity duration-300"
			leave-active-class="transition-opacity duration-200"
		>
			<div
				v-if="uiStore.sidebarOpen"
				@click="uiStore.toggleSidebar"
				class="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
			/>
		</transition>

		<!-- Sidebar -->
		<aside
			:class="[
				'fixed lg:relative z-50 lg:z-auto',
				'w-72 lg:w-64 bg-surface-elevated border-r border-border',
				'flex flex-col h-full transform transition-transform duration-300 ease-in-out',
				uiStore.sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
			]"
		>
			<!-- Logo Section -->
			<div class="p-6 border-b border-border flex-shrink-0">
				<div class="flex items-center gap-3 mb-1">
					<div
						class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center shadow-lg shadow-primary-500/20"
					>
						<span class="text-white font-bold text-lg">NO</span>
					</div>
					<div>
						<h1 class="text-xl font-bold text-white">National Oil</h1>
						<p class="text-xs text-gray-500">Management System</p>
					</div>
				</div>
			</div>

			<!-- Navigation Menu -->
			<nav class="flex-1 overflow-y-auto pt-4 pb-4 px-3">
				<SidebarMenu />
			</nav>

			<!-- Footer Actions -->
			<div class="p-4 border-t border-border flex-shrink-0 space-y-2">
				<button
					@click="showAbout = true"
					class="w-full text-left px-4 py-2 text-xs text-gray-400 hover:text-gray-300 rounded-xl hover:bg-surface transition-colors flex items-center gap-2"
				>
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
						/>
					</svg>
					Version 1.0.0
				</button>
			</div>
		</aside>

		<!-- Main Content Area -->
		<div class="flex-1 flex flex-col overflow-hidden lg:ml-0">
			<!-- Topbar -->
			<Topbar @menu-click="uiStore.toggleSidebar" />

			<!-- Page Content -->
			<main class="flex-1 overflow-y-auto bg-surface">
				<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
					<RouterView />
				</div>
			</main>
		</div>

		<!-- About Modal -->
		<transition
			enter-active-class="transition duration-300 ease-out"
			leave-active-class="transition duration-200 ease-in"
			enter-from-class="opacity-0 scale-95"
			enter-to-class="opacity-100 scale-100"
			leave-from-class="opacity-100 scale-100"
			leave-to-class="opacity-0 scale-95"
		>
			<div
				v-if="showAbout"
				class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
			>
				<Card class="max-w-sm w-full mx-4">
					<template #header>
						<div class="flex items-center gap-3">
							<div
								class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center"
							>
								<span class="text-white font-bold text-lg">NO</span>
							</div>
							<div>
								<h2 class="text-lg font-bold text-white">National Oil System</h2>
								<p class="text-xs text-gray-500">v1.0.0</p>
							</div>
						</div>
					</template>

					<p class="text-sm text-gray-400 mb-6">
						A comprehensive petrol station management system built with Vue 3 and
						Frappe.
					</p>

					<Button @click="showAbout = false" variant="primary" full-width>
						Close
					</Button>
				</Card>
			</div>
		</transition>
	</div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useUIStore } from "@/stores/ui";
import { RouterView } from "vue-router";
import Topbar from "@/components/layout/Topbar.vue";
import SidebarMenu from "@/components/layout/SidebarMenu.vue";
import Card from "@/components/ui/Card.vue";
import Button from "@/components/ui/Button.vue";

const authStore = useAuthStore();
const uiStore = useUIStore();
const showAbout = ref(false);
</script>

<style scoped>
/* Smooth transitions for mobile sidebar */
@media (max-width: 1023px) {
	.fixed.lg\:relative {
		position: fixed;
	}
}
</style>
