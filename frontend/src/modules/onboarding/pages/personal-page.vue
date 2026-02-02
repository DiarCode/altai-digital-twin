<script setup lang="ts">
import { Button } from '@/core/components/ui/button'
import { ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const gender = ref<'male' | 'female' | ''>('')
const birthDate = ref('')
const step = ref<1 | 2>(1)

const birthDateInput = ref<HTMLInputElement | null>(null)

const goNext = () => {
  if (!gender.value) return
  step.value = 2
  nextTick(() => {
    birthDateInput.value?.focus()
  })
}

const handleSubmit = () => {
  if (!birthDate.value.trim()) return
  router.push('/onboarding/face')
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
          <!-- STEP 1: GENDER -->
          <div v-if="step === 1" key="step-gender" class="space-y-10">
            <div class="space-y-3">
              <label class="text-[24px] text-slate-900 font-semibold">Gender</label>

              <select
                v-model="gender"
                @keyup.enter="goNext"
                class="w-full text-[24px] px-0 py-4 focus:outline-none rounded-none mt-2 border-transparent border-b border-b-slate-200 shadow-none focus:border-b-slate-900 transition-colors bg-transparent"
              >
                <option value="" disabled>Select your gender</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
              </select>
            </div>

            <div class="flex items-center justify-between pt-4">
              <div class="flex items-center gap-3">
                <Button
                  @click="goNext"
                  :disabled="!gender"
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

          <!-- STEP 2: BIRTH DATE -->
          <div v-else key="step-birthdate" class="space-y-10">
            <div class="space-y-3">
              <label class="text-[24px] text-slate-900 font-semibold">Birth date</label>

              <input
                ref="birthDateInput"
                v-model="birthDate"
                type="date"
                placeholder="Enter your birth date"
                @keyup.enter="handleSubmit"
                class="w-full text-[24px] px-0 py-4 focus:outline-none rounded-none mt-2 border-transparent border-b border-b-slate-200 shadow-none focus:border-b-slate-900 transition-colors"
              />
            </div>

            <div class="flex items-center justify-between pt-4">
              <div class="flex items-center gap-3">
                <Button
                  @click="handleSubmit"
                  :disabled="!birthDate.trim()"
                  class="text-[20px] px-10 py-6 tracking-wide disabled:opacity-60 disabled:cursor-not-allowed"
                >
                  Submit
                </Button>
                <span class="text-[14px] text-slate-500">
                  press <span class="font-mono font-medium">Enter ↵</span>
                </span>
              </div>

              <button
                type="button"
                class="text-sm text-slate-500 hover:text-slate-800 underline-offset-4 hover:underline"
                @click="step = 1"
              >
                Back
              </button>
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
