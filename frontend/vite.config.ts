import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vitest/config';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		port: 5173,
		proxy: {
			'/api': {
				target: 'http://127.0.0.1:8000',
				changeOrigin: true
			},
			'/health': {
				target: 'http://127.0.0.1:8000',
				changeOrigin: true
			}
		}
	},
	test: {
		environment: 'jsdom',
		globals: true
	}
});
