/**
 * Estado global compartido entre features (Zustand).
 * Solo para estado del cliente: auth, carrito, UI global.
 * No usar para datos del servidor (usar React Query / SWR en hooks).
 */

import { create } from "zustand";

interface GlobalState {
  lastAction: string | null;
  setLastAction: (action: string | null) => void;
}

export const useStore = create<GlobalState>((set) => ({
  lastAction: null,
  setLastAction: (action) => set({ lastAction: action }),
}));
