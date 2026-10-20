/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],
	theme: {
		extend: {
			colors: {
				citu: {
					red: '#C62828',
					'red-dark': '#B71C1C',
					'red-light': '#EF5350',
					gold: '#F59E0B',
					'gold-light': '#FEF3C7',
					slate: '#1E293B',
					'slate-dark': '#0F172A',
					bg: '#F8FAFC'
				}
			},
			fontFamily: {
				sans: ['"Noto Sans"', '"Noto Sans Malayalam"', 'sans-serif'],
				malayalam: ['"Noto Sans Malayalam"', 'sans-serif']
			}
		}
	},
	plugins: []
};
