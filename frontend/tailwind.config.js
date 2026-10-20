/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],
	theme: {
		extend: {
			colors: {
				primary: '#a10014',
				'on-primary': '#ffffff',
				'primary-container': '#c81d25',
				'on-primary-container': '#ffddda',
				'inverse-primary': '#ffb3ad',
				'primary-fixed': '#ffdad6',
				'primary-fixed-dim': '#ffb3ad',
				'on-primary-fixed': '#410003',
				'on-primary-fixed-variant': '#930011',
				surface: '#f9f9ff',
				'surface-dim': '#d3daef',
				'surface-bright': '#f9f9ff',
				'surface-container-lowest': '#ffffff',
				'surface-container-low': '#f1f3ff',
				'surface-container': '#e9edff',
				'surface-container-high': '#e1e8fd',
				'surface-container-highest': '#dce2f7',
				'surface-variant': '#dce2f7',
				'on-surface': '#141b2b',
				'on-surface-variant': '#5c403d',
				'inverse-surface': '#293040',
				'inverse-on-surface': '#edf0ff',
				'surface-tint': '#bc111e',
				secondary: '#555f6d',
				'on-secondary': '#ffffff',
				'secondary-container': '#d6e0f1',
				'on-secondary-container': '#596372',
				'secondary-fixed': '#d9e3f4',
				'secondary-fixed-dim': '#bdc7d8',
				'on-secondary-fixed': '#121c28',
				'on-secondary-fixed-variant': '#3e4755',
				tertiary: '#2e4999',
				'on-tertiary': '#ffffff',
				'tertiary-container': '#4861b3',
				'on-tertiary-container': '#dfe3ff',
				'tertiary-fixed': '#dce1ff',
				'tertiary-fixed-dim': '#b6c4ff',
				'on-tertiary-fixed': '#00164e',
				'on-tertiary-fixed-variant': '#264191',
				outline: '#906f6c',
				'outline-variant': '#e5bdba',
				error: '#ba1a1a',
				'on-error': '#ffffff',
				'error-container': '#ffdad6',
				'on-error-container': '#93000a',
				background: '#f9f9ff',
				'on-background': '#141b2b',
				citu: {
					red: '#a10014',
					'red-dark': '#80000f',
					'red-light': '#c81d25',
					gold: '#F59E0B',
					'gold-light': '#FEF3C7',
					slate: '#141b2b',
					'slate-dark': '#0F172A',
					bg: '#f9f9ff'
				}
			},
			spacing: {
				'space-xs': '0.25rem',
				'space-sm': '0.5rem',
				'space-md': '1rem',
				'space-lg': '1.5rem',
				'space-xl': '2.5rem',
				gutter: '1.5rem',
				'gutter-mobile': '1rem',
				margin: '2rem',
				'margin-mobile': '1rem'
			},
			fontFamily: {
				sans: ['Inter', '"Noto Sans Malayalam"', 'sans-serif'],
				malayalam: ['"Noto Sans Malayalam"', 'sans-serif']
			}
		}
	},
	plugins: []
};
