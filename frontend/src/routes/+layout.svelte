<script lang="ts">
	import '../app.css';
	import { currentLanguage, setLanguage, translations } from '$lib/i18n';

	let { children } = $props();

	let lang = $state('ml');
	currentLanguage.subscribe((val) => {
		lang = val;
	});

	function toggleLang() {
		const next = lang === 'ml' ? 'en' : 'ml';
		setLanguage(next);
	}
</script>

<div class="min-h-screen flex flex-col bg-slate-50">
	<!-- CITU Kerala Header -->
	<header class="bg-citu-red text-white shadow-md sticky top-0 z-50">
		<div class="max-w-2xl mx-auto px-4 py-3 flex items-center justify-between">
			<div class="flex items-center space-x-3">
				<!-- CITU Solidarity Star & Emblem Icon -->
				<div class="w-10 h-10 rounded-full bg-white flex items-center justify-center text-citu-red font-bold text-xl shadow-inner">
					★
				</div>
				<div>
					<h1 class="text-sm sm:text-base font-bold leading-tight tracking-wide">
						{translations[lang as 'ml' | 'en'].unionShort}
					</h1>
					<p class="text-xs text-red-100 hidden sm:block">
						{translations[lang as 'ml' | 'en'].unionTitle}
					</p>
				</div>
			</div>

			<!-- Language Switcher Pill -->
			<button
				onclick={toggleLang}
				class="touch-target px-3 py-1.5 rounded-full bg-red-800/60 hover:bg-red-800 text-xs font-semibold text-yellow-300 border border-yellow-400/40 flex items-center space-x-1 transition active:scale-95"
				aria-label="Switch Language"
			>
				<span>{lang === 'ml' ? 'മലയാളം' : 'English'}</span>
				<span class="text-white/60">|</span>
				<span class="text-white font-normal">{lang === 'ml' ? 'EN' : 'മല'}</span>
			</button>
		</div>
	</header>

	<!-- Main Container -->
	<main class="flex-1 max-w-2xl w-full mx-auto px-4 py-6">
		{@render children?.()}
	</main>

	<!-- Footer -->
	<footer class="bg-citu-slate-dark text-slate-300 py-6 border-t border-slate-800 mt-auto text-center text-xs">
		<div class="max-w-2xl mx-auto px-4 space-y-2">
			<p class="text-red-400 font-bold uppercase tracking-wider">
				{translations[lang as 'ml' | 'en'].tagline}
			</p>
			<p class="text-slate-400">
				Kerala State Committee | Centre of Indian Trade Unions (CITU)
			</p>
			<p class="text-slate-400 text-[11px]">
				AKG Centre, Palayam, Thiruvananthapuram, Kerala
			</p>
		</div>
	</footer>
</div>
