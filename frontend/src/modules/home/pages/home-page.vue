<script setup lang="ts">
import avatar from '@/core/assets/avatar.png'
import { Button } from '@/core/components/ui/button'
import {
  Layers,
  MessageCircle,
  MessageSquare,
  Mic,
  MoreVertical,
  Send,
  Settings,
} from 'lucide-vue-next'
import { ref } from 'vue'

interface Persona {
  id: number
  avatar: string
}

const persona: Persona = { id: 1, avatar: avatar }

const isVoiceMode = ref(false)
const isChatOpen = ref(false)
const isListening = ref(false)
const message = ref('')
const messages = ref<Array<{ text: string; isUser: boolean }>>([])
const isAnimating = ref(false)

const toggleVoice = () => {
  isVoiceMode.value = !isVoiceMode.value
  isChatOpen.value = false
  isListening.value = isVoiceMode.value
}

const toggleChat = () => {
  isChatOpen.value = !isChatOpen.value
  isVoiceMode.value = false
  isListening.value = false
}

const sendMessage = () => {
  if (!message.value.trim()) return
  messages.value.push({ text: message.value, isUser: true })
  setTimeout(() => messages.value.push({ text: '…', isUser: false }), 800)
  message.value = ''
}
</script>

<template>
  <div class="relative w-screen h-screen bg-white text-gray-900 overflow-hidden">
    <!-- Background with large orbs -->
    <div class="absolute inset-0 z-0 overflow-hidden">
      <div class="absolute inset-0 bg-linear-to-br from-gray-100 via-white to-indigo-50"></div>

      <!-- Large decorative orbs -->
      <div
        class="absolute top-0 left-0 w-96 h-96 bg-purple-200 rounded-full mix-blend-multiply filter blur-3xl opacity-40 animate-float"
        style="animation-duration: 20s; animation-delay: 0s"
      ></div>
      <div
        class="absolute top-0 right-0 w-[500px] h-[500px] bg-blue-200 rounded-full mix-blend-multiply filter blur-3xl opacity-40 animate-float"
        style="animation-duration: 25s; animation-delay: -5s"
      ></div>
      <div
        class="absolute bottom-0 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-pink-200 rounded-full mix-blend-multiply filter blur-3xl opacity-40 animate-float"
        style="animation-duration: 30s; animation-delay: -10s"
      ></div>

      <!-- Smaller accent orbs -->
      <div
        v-for="i in 8"
        :key="i"
        class="absolute rounded-full mix-blend-multiply filter blur-2xl opacity-30"
        :class="i % 3 === 0 ? 'bg-purple-100' : i % 3 === 1 ? 'bg-blue-100' : 'bg-pink-100'"
        :style="{
          width: `${150 + Math.random() * 200}px`,
          height: `${150 + Math.random() * 200}px`,
          left: `${Math.random() * 100}%`,
          top: `${Math.random() * 100}%`,
          animationDelay: `${Math.random() * 20}s`,
          animationDuration: `${20 + Math.random() * 10}s`,
        }"
      ></div>
    </div>

    <!-- Header -->
    <header class="absolute top-8 left-8 right-8 z-20 flex justify-between">
      <Button variant="ghost" size="icon">
        <Layers class="size-7 text-black" />
      </Button>
      <Button variant="ghost" size="icon">
        <Settings class="size-7 text-black" />
      </Button>
    </header>

    <!-- Avatar Carousel -->
    <main class="absolute inset-0 z-10 flex items-center justify-center">
      <div
        class="relative w-full h-full transform-style-3d perspective-3000px"
        :class="{ 'is-animating': isAnimating }"
      >
        <div
          class="absolute bottom-0 left-1/2 w-auto -translate-x-1/2 transition-all duration-500 cursor-pointer"
        >
          <div
            class="absolute -inset-[120px] bg-[radial-gradient(circle_at_center,rgba(59,130,246,0.4)_0%,transparent_70%)] opacity-70 transition-opacity duration-300 rounded-[2.5rem] blur-3xl z-0 animate-glow-pulse"
          ></div>
          <img
            :src="persona.avatar"
            class="h-[90vh] w-full object-cover rounded-3xl relative z-10"
          />
          <div
            class="absolute inset-0 rounded-2xl bg-linear-to-r from-transparent via-white/5 to-transparent opacity-0 animate-shimmer z-20"
          ></div>
        </div>
      </div>
    </main>

    <!-- Interaction Panel -->
    <footer class="absolute bottom-0 left-0 right-0 z-20 p-8">
      <Transition name="slide-up">
        <div v-if="isChatOpen && messages.length" class="max-w-2xl mx-auto mb-6">
          <div class="max-h-72 overflow-y-auto px-2 flex flex-col gap-4">
            <div
              v-for="(msg, idx) in messages"
              :key="idx"
              class="flex animate-slide-in"
              :class="msg.isUser ? 'justify-end' : 'justify-start'"
            >
              <div
                class="max-w-[80%] px-4 py-3 rounded-xl text-base leading-relaxed backdrop-blur-lg"
                :class="
                  msg.isUser
                    ? 'bg-blue-500/90 text-black'
                    : 'bg-white/5 text-black border border-white/10'
                "
              >
                {{ msg.text }}
              </div>
            </div>
          </div>
        </div>
      </Transition>

      <Transition name="slide-up">
        <div v-if="isChatOpen" class="max-w-2xl mx-auto mb-6 flex gap-4">
          <input
            v-model="message"
            type="text"
            class="flex-1 px-6 py-4 bg-white/5 border border-white/10 rounded-xl text-black text-base backdrop-blur-lg focus:outline-none focus:border-blue-500/50 focus:bg-white/8"
            @keyup.enter="sendMessage"
          />
          <button
            @click="sendMessage"
            class="w-12 h-12 rounded-xl bg-blue-500 border-none cursor-pointer flex items-center justify-center transition-all duration-300 hover:scale-105"
          >
            <Send class="w-5 h-5 text-black" />
          </button>
        </div>
      </Transition>

      <Transition name="fade">
        <div
          v-if="isVoiceMode && isListening"
          class="max-w-2xl mx-auto mb-6 p-8 flex justify-center items-center"
        >
          <div class="flex gap-2 items-center h-16">
            <div
              v-for="i in 5"
              :key="i"
              class="w-1 bg-indigo-500 rounded-sm animate-wave"
              :style="{ animationDelay: `${i * 0.1}s` }"
            ></div>
          </div>
        </div>
      </Transition>

      <div
        class="mx-auto flex justify-center items-center gap-6 bg-primary/30 backdrop-blur-md shadow-xl w-fit p-4 rounded-full"
      >
        <button
          class="relative w-14 h-14 rounded-full bg-white backdrop-blur-lg border border-white/10 cursor-pointer transition-all duration-300 flex items-center justify-center text-black hover:bg-white/70"
        >
          <MessageCircle class="w-6 h-6" />
        </button>

        <button
          @click="toggleVoice"
          class="relative w-14 h-14 rounded-full bg-white backdrop-blur-lg border border-white/10 cursor-pointer transition-all duration-300 flex items-center justify-center text-black hover:bg-white/70"
          :class="{ active: isVoiceMode }"
        >
          <Mic class="w-7 h-7" />
        </button>

        <button
          @click="toggleChat"
          class="relative w-14 h-14 rounded-full bg-white backdrop-blur-lg border border-white/10 cursor-pointer transition-all duration-300 flex items-center justify-center text-black hover:bg-white/70"
          :class="{ active: isChatOpen }"
        >
          <MessageSquare class="w-7 h-7" />
        </button>

        <button
          class="relative w-14 h-14 rounded-full bg-white backdrop-blur-lg border border-white/10 cursor-pointer transition-all duration-300 flex items-center justify-center text-black hover:bg-white/70"
        >
          <MoreVertical class="w-6 h-6" />
        </button>
      </div>
    </footer>
  </div>
</template>

<style>
/* Custom animations that can't be replaced with Tailwind */
@keyframes float {
  0%,
  100% {
    opacity: 0;
    transform: translateY(100vh) translateX(0);
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(-100vh) translateX(50px);
  }
}

@keyframes glow-pulse {
  0%,
  100% {
    opacity: 0.4;
  }
  50% {
    opacity: 0.8;
    transform: scale(1.05);
  }
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

@keyframes wave {
  0%,
  100% {
    height: 20px;
  }
  50% {
    height: 50px;
  }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-float {
  animation: float 15s linear infinite;
}

.animate-glow-pulse {
  animation: glow-pulse 3s ease-in-out infinite;
}

.animate-shimmer {
  animation: shimmer 3s ease-in-out infinite;
}

.animate-wave {
  animation: wave 1.2s ease-in-out infinite;
}

.animate-slide-in {
  animation: slideIn 0.3s ease;
}

/* Additional utility classes */
.transform-style-3d {
  transform-style: preserve-3d;
}

.perspective-3000px {
  perspective: 3000px;
}

/* Hide scrollbar for messages */
.max-h-72::-webkit-scrollbar {
  width: 6px;
}

.max-h-72::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
}

.max-h-72::-webkit-scrollbar-thumb {
  background: rgba(59, 130, 246, 0.5);
  border-radius: 3px;
}

/* Active control button state */
.active {
  background: rgb(171, 59, 246) !important;
  border-color: rgb(168, 59, 246) !important;
  color: white !important;
  transform: translateY(-4px) scale(1.1) !important;
}
</style>
