<script setup lang="ts">
import { Button } from '@/core/components/ui/button'
import { useRouter } from 'vue-router'

const router = useRouter()

const handleProceed = () => {
  router.push('/login')
}
</script>

<template>
  <div
    class="min-h-screen w-full flex items-center justify-center bg-white relative overflow-hidden"
  >
    <!-- Floating orbs -->
    <div
      class="absolute -top-32 -left-32 size-96 opacity-30 blur-3xl rounded-full bg-primary"
    ></div>
    <div
      class="absolute top-40 right-32 size-96 opacity-30 blur-3xl rounded-full bg-blue-300"
    ></div>
    <div
      class="absolute bottom-32 right-20 size-96 opacity-30 blur-3xl rounded-full bg-primary/60"
    ></div>
    <div
      class="absolute bottom-20 left-40 size-96 opacity-30 blur-3xl rounded-full bg-blue-400"
    ></div>

    <div class="w-full max-w-6xl mx-auto px-8 flex flex-col items-center gap-12">
      <!-- Content -->
      <div class="flex flex-col items-center text-center space-y-8 z-10">
        <div class="space-y-6">
          <h1 class="text-[48px] lg:text-[64px] font-bold tracking-tight text-black leading-tight">
            Experience the Future<br />
            of Digital Twins
          </h1>

          <p class="text-[24px] text-slate-600 max-w-2xl mx-auto">
            Create your AI-powered digital twin
          </p>
        </div>

        <Button
          size="lg"
          class="text-[18px] px-12 py-6 text-white font-semibold tracking-wide"
          @click="handleProceed"
        >
          Get Started
        </Button>
      </div>

      <!-- Robot Display Card -->
      <div class="relative w-full max-w-3xl">
        <!-- Glassmorphic container -->
        <div
          class="relative rounded-3xl border border-slate-100 shadow-xl bg-slate-200/10 backdrop-blur-sm overflow-visible"
        >
          <!-- Robot Image -->
          <div class="relative z-10 flex items-center justify-center">
            <img src="@/core/assets/robot.png" alt="Digital Twin" class="w-full max-w-xl h-auto" />
          </div>

          <!-- Status Badge -->
          <div class="absolute bottom-6 left-1/2 -translate-x-1/2 z-20">
            <div
              class="flex items-center gap-3 px-6 py-3 rounded-full bg-white/90 backdrop-blur-xl border border-slate-200"
            >
              <div class="w-2 h-2 rounded-full bg-primary animate-pulse"></div>
              <span class="text-black text-[16px] font-medium">AI Processing</span>
            </div>
          </div>
        </div>

        <!-- Floating Badges around image -->
        <!-- Top Left -->
        <div class="absolute top-28 left-32 z-30">
          <div
            class="flex items-center gap-3 px-5 py-3 rounded-xl bg-white border border-slate-200 shadow-lg"
          >
            <div class="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
              <svg
                class="w-4 h-4 text-primary"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <span class="text-[16px] font-medium text-black">3D Scan</span>
          </div>
        </div>

        <!-- Top Right -->
        <div class="absolute top-20 right-32 z-30">
          <div
            class="flex items-center gap-3 px-5 py-3 rounded-xl bg-white border border-slate-200 shadow-lg"
          >
            <div class="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
              <svg
                class="w-4 h-4 text-primary"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            </div>
            <span class="text-[16px] font-medium text-black">AI Voice</span>
          </div>
        </div>

        <!-- Bottom Right -->
        <div class="absolute bottom-32 right-14 z-30">
          <div
            class="flex items-center gap-3 px-5 py-3 rounded-xl bg-white border border-slate-200 shadow-lg"
          >
            <div class="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
              <svg
                class="w-4 h-4 text-primary"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
                />
              </svg>
            </div>
            <span class="text-[16px] font-medium text-black">Clone Memory</span>
          </div>
        </div>

        <!-- Left -->
        <div class="absolute top-60 left-18 z-30">
          <div
            class="flex items-center gap-3 px-5 py-3 rounded-xl bg-white border border-slate-200 shadow-lg"
          >
            <div class="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
              <svg
                class="w-4 h-4 text-primary"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z"
                />
              </svg>
            </div>
            <span class="text-[16px] font-medium text-black">Chat AI</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
