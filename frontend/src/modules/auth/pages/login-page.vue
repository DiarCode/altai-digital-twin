<script setup lang="ts">
import { Button } from '@/core/components/ui/button'
import { ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const username = ref('')
const password = ref('')
const step = ref<1 | 2>(1)

const passwordInput = ref<HTMLInputElement | null>(null)

const goNext = () => {
  if (!username.value.trim()) return
  step.value = 2
  nextTick(() => {
    passwordInput.value?.focus()
  })
}

const handleLogin = () => {
  if (!password.value.trim()) return
  router.push('/onboarding/personal')
}
</script>

<template>
  <div class="min-h-screen w-full flex flex-col bg-white relative overflow-hidden">
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

    <!-- Logo -->
    <div class="absolute top-8 left-8 z-10">
      <span class="text-[28px] font-bold text-black">Altai</span>
    </div>

    <!-- Main Content -->
    <div class="flex-1 flex items-center justify-center px-8 relative z-10">
      <div class="w-full max-w-3xl space-y-10">
        <Transition name="fade-step" mode="out-in">
          <!-- STEP 1: USERNAME -->
          <div v-if="step === 1" key="step-username" class="space-y-10">
            <div class="space-y-3">
              <label class="text-[24px] text-slate-900 font-semibold">Username</label>

              <input
                v-model="username"
                type="text"
                placeholder="Enter your username"
                @keyup.enter="goNext"
                class="w-full text-[24px] px-0 py-4 focus:outline-none rounded-none mt-2 border-transparent border-b border-b-slate-200 shadow-none focus:border-b-slate-900 transition-colors"
              />
            </div>

            <div class="flex items-center justify-between pt-4">
              <div class="flex items-center gap-3">
                <Button
                  @click="goNext"
                  :disabled="!username.trim()"
                  class="text-[20px] px-10 py-6 tracking-wide disabled:opacity-60 disabled:cursor-not-allowed"
                >
                  Next
                </Button>
                <span class="text-[14px] text-slate-500">
                  press <span class="font-mono font-medium">Enter ↵</span>
                </span>
              </div>
            </div>
          </div>

          <!-- STEP 2: PASSWORD -->
          <div v-else key="step-password" class="space-y-10">
            <div class="space-y-3">
              <label class="text-[24px] text-slate-900 font-semibold">Password</label>

              <input
                ref="passwordInput"
                v-model="password"
                type="password"
                placeholder="Enter your password"
                @keyup.enter="handleLogin"
                class="w-full text-[24px] px-0 py-4 focus:outline-none rounded-none mt-2 border-transparent border-b border-b-slate-200 shadow-none focus:border-b-slate-900 transition-colors"
              />
            </div>

            <div class="flex items-center justify-between pt-4">
              <div class="flex items-center gap-3">
                <Button
                  @click="handleLogin"
                  :disabled="!password.trim()"
                  class="text-[20px] px-10 py-6 tracking-wide disabled:opacity-60 disabled:cursor-not-allowed"
                >
                  Login
                </Button>
                <span class="text-[14px] text-slate-500">
                  press <span class="font-mono font-medium">Enter ↵</span>
                </span>
              </div>

              <Button
                variant="ghost"
                type="button"
                class="text-slate-500 text-lg hover:bg-transparent hover:text-slate-800 underline-offset-4 hover:underline"
                @click="step = 1"
              >
                Back
              </Button>
            </div>
          </div>
        </Transition>
      </div>
    </div>
  </div>
</template>

<style scoped>
.fade-step-enter-active,
.fade-step-leave-active {
  transition:
    opacity 0.25s ease,
    transform 0.25s ease;
}
.fade-step-enter-from,
.fade-step-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>
