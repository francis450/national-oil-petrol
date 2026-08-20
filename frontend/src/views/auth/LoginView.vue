<template>
	<div class="min-h-screen bg-surface flex items-center justify-center px-4 sm:px-6 lg:px-8">
		<div class="w-full max-w-md">
			<!-- Logo Card -->
			<Card class="mb-8 text-center animate-fade-in">
				<div class="flex flex-col items-center gap-3">
					<div
						class="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center shadow-lg shadow-primary-500/20"
					>
						<span class="text-white text-2xl font-bold">NO</span>
					</div>
					<h1 class="text-3xl font-bold text-white">National Oil</h1>
					<p class="text-gray-400">Petrol Station Management System</p>
				</div>
			</Card>

			<!-- Login Form -->
			<Card class="animate-slide-up" style="animation-delay: 0.1s">
				<template #header>
					<h2 class="text-2xl font-bold text-white text-center">Sign In</h2>
				</template>

				<form @submit.prevent="handleLogin" class="space-y-5">
					<!-- Username Input -->
					<Input
						v-model="username"
						label="Username"
						placeholder="Enter your username"
						required
						:error="errors.username"
					/>

					<!-- Password Input -->
					<Input
						v-model="password"
						label="Password"
						type="password"
						placeholder="Enter your password"
						required
						:error="errors.password"
					/>

					<!-- Error Message -->
					<div
						v-if="error"
						class="p-4 bg-danger-600/10 border border-danger-600/20 rounded-xl text-danger-400 text-sm"
					>
						{{ error }}
					</div>

					<!-- Submit Button -->
					<Button
						type="submit"
						variant="primary"
						full-width
						:loading="loading"
						size="lg"
					>
						{{ loading ? "Signing in..." : "Sign In" }}
					</Button>
				</form>
			</Card>

			<!-- Footer -->
			<p class="text-center text-gray-500 text-sm mt-8">
				&copy; {{ new Date().getFullYear() }} National Oil. All rights reserved.
			</p>
		</div>
	</div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import Card from "@/components/ui/Card.vue";
import Input from "@/components/ui/Input.vue";
import Button from "@/components/ui/Button.vue";

const router = useRouter();
const authStore = useAuthStore();

const username = ref("");
const password = ref("");
const loading = ref(false);
const error = ref("");

const errors = reactive({
	username: "",
	password: "",
});

/**
 * Validate form inputs
 */
const validateForm = (): boolean => {
	let isValid = true;

	if (!username.value.trim()) {
		errors.username = "Username is required";
		isValid = false;
	} else {
		errors.username = "";
	}

	if (!password.value.trim()) {
		errors.password = "Password is required";
		isValid = false;
	} else {
		errors.password = "";
	}

	return isValid;
};

/**
 * Handle login form submission
 */
const handleLogin = async () => {
	if (!validateForm()) return;

	loading.value = true;
	error.value = "";

	try {
		await authStore.login(username.value, password.value);
		// If login succeeds, auth store is updated automatically
		// Redirect to dashboard
		router.push("/");
	} catch (err: any) {
		error.value = err.message || "Login failed. Please try again.";
		console.error("Login error:", err);
	} finally {
		loading.value = false;
	}
};

/**
 * On mount: If user already has a session, skip login form
 */
onMounted(async () => {
	if (authStore.isAuthenticated) {
		router.push("/");
	}
});
</script>

<style scoped></style>
