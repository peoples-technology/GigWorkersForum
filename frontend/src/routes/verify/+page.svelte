<script lang="ts">
	import { goto } from '$app/navigation';

	let lang = $state<'ml' | 'en'>('ml');
	let searchInput = $state('');

	function handleLookup() {
		if (searchInput.trim()) {
			goto(`/verify/${encodeURIComponent(searchInput.trim().toUpperCase())}`);
		}
	}
</script>

<svelte:head>
	<title>{lang === 'ml' ? 'പൊതു അംഗത്വ പരിശോധന | GigWorkers.Online' : 'Public Member Verification | GigWorkers.Online'}</title>
</svelte:head>

<!-- Sticky Header -->
<header class="fixed top-0 w-full z-50 bg-white/90 backdrop-blur-md shadow-sm border-b border-slate-200/80">
	<div class="h-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between">
		<a href="/" class="flex items-center gap-3">
			<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-red-600 via-primary to-red-900 flex items-center justify-center text-white font-bold text-lg shadow-sm shrink-0">
				★
			</div>
			<div class="flex flex-col">
				<div class="flex items-center gap-2">
					<span class="text-sm sm:text-base tracking-tight text-slate-900 uppercase font-black">GigWorkers.Online</span>
					<span class="hidden sm:inline-block px-2 py-0.5 rounded-full bg-red-100 text-red-800 text-[10px] uppercase font-bold">
						Trade Union
					</span>
				</div>
				<span class="text-xs text-slate-500 font-medium">
					{lang === 'ml' ? 'അംഗത്വ പരിശോധന / Member Verification' : 'Public Member Verification'}
				</span>
			</div>
		</a>

		<div class="flex items-center gap-3">
			<div class="inline-flex items-center bg-slate-100 border border-slate-200 rounded-full p-1 shadow-inner">
				<button 
					type="button" 
					onclick={() => lang = 'ml'}
					class={`px-3 py-1 rounded-full text-xs font-bold transition-all ${lang === 'ml' ? 'bg-primary text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'}`}
				>
					മലയാളം
				</button>
				<button 
					type="button" 
					onclick={() => lang = 'en'}
					class={`px-3 py-1 rounded-full text-xs font-bold transition-all ${lang === 'en' ? 'bg-primary text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'}`}
				>
					EN
				</button>
			</div>

			<a href="/" class="text-xs font-bold text-slate-600 hover:text-primary transition">
				Home
			</a>
		</div>
	</div>
</header>

<main class="w-full pt-28 hero-gradient-mesh min-h-[calc(100vh-80px)] flex flex-col items-center px-4">
	<div class="max-w-lg w-full card-gloss rounded-3xl shadow-2xl border border-slate-200/90 p-6 sm:p-9 text-center">
		<div class="w-16 h-16 rounded-2xl bg-red-100 text-primary flex items-center justify-center mx-auto mb-4 shadow-sm">
			<span class="material-symbols-outlined text-3xl">qr_code_scanner</span>
		</div>

		<h1 class="text-xl sm:text-2xl font-black text-slate-900">
			{lang === 'ml' ? 'അംഗത്വ കാർഡ് പരിശോധിക്കുക' : 'Verify Union Membership'}
		</h1>
		<p class="text-xs sm:text-sm text-slate-500 mt-1 max-w-sm mx-auto font-medium">
			{lang === 'ml'
				? 'ക്യുആർ കോഡ് സ്കാൻ ചെയ്യുകയോ അംഗത്വ നമ്പർ നൽകുകയോ ചെയ്യുക.'
				: 'Scan member QR code or enter membership registration number.'}
		</p>

		<!-- Search Input Form -->
		<form onsubmit={(e) => { e.preventDefault(); handleLookup(); }} class="mt-6 flex flex-col gap-3">
			<div class="relative flex items-center">
				<span class="material-symbols-outlined absolute left-3.5 text-slate-400 text-[20px]">badge</span>
				<input 
					type="text" 
					bind:value={searchInput}
					placeholder="e.g. KLTVC000009 or KLERN000142" 
					class="w-full h-12 pl-11 pr-3 rounded-xl border border-slate-300 bg-white text-slate-900 font-mono font-bold tracking-wider text-sm focus:ring-2 focus:ring-primary focus:outline-none shadow-xs"
				/>
			</div>

			<button 
				type="submit" 
				class="w-full py-3.5 rounded-xl crimson-gradient-btn text-white font-bold text-sm shadow-md transition flex items-center justify-center gap-2"
			>
				<span class="material-symbols-outlined text-[18px]">verified</span>
				<span>{lang === 'ml' ? 'പരിശോധിക്കുക' : 'Verify Credentials'}</span>
			</button>
		</form>

		<!-- Sample Verification Quick Links -->
		<div class="mt-6 pt-5 border-t border-surface-variant text-left">
			<span class="text-xs text-secondary font-semibold block mb-2">
				{lang === 'ml' ? 'സാമ്പിൾ ഐഡികൾ പരിശോധിക്കുക:' : 'Sample Active Records:'}
			</span>
			<div class="flex flex-wrap gap-2">
				<a href="/verify/KLTVC000009" class="px-3 py-1 rounded bg-surface-container hover:bg-surface-container-high text-xs font-mono font-semibold text-primary">
					KLTVC000009 (Zomato)
				</a>
				<a href="/verify/KLERN000142" class="px-3 py-1 rounded bg-surface-container hover:bg-surface-container-high text-xs font-mono font-semibold text-primary">
					KLERN000142 (Uber)
				</a>
				<a href="/verify/KLKZD000219" class="px-3 py-1 rounded bg-surface-container hover:bg-surface-container-high text-xs font-mono font-semibold text-primary">
					KLKZD000219 (Swiggy)
				</a>
			</div>
		</div>

		<!-- DPDP Notice -->
		<div class="mt-6 p-3 rounded-lg bg-surface-container-low text-[11px] text-secondary text-left flex items-start gap-2 border border-surface-variant">
			<span class="material-symbols-outlined text-[15px] shrink-0 text-secondary mt-0.5">privacy_tip</span>
			<span><strong>DPDP Act 2023 Compliant:</strong> Zero personal contact details disclosed. Public verification validates union accreditation only.</span>
		</div>
	</div>
</main>

<footer class="w-full bg-surface-container-lowest border-t border-surface-variant py-6 mt-12 text-center text-xs text-secondary">
	GigWorkers.Online · Kerala Gig &amp; Platform Workers Union (CITU)
</footer>
