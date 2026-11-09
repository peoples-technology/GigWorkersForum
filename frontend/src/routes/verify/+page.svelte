<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import VerifyCardView from '$lib/VerifyCardView.svelte';
	import Icon from '$lib/Icon.svelte';

	let lang = $state<'ml' | 'en'>('ml');
	let searchInput = $state('');

	let queryToken = $derived(
		$page.url.searchParams.get('token') || 
		$page.url.searchParams.get('id') || 
		''
	);

	function handleLookup() {
		if (searchInput.trim()) {
			goto(`/verify?token=${encodeURIComponent(searchInput.trim().toUpperCase())}`);
		}
	}
</script>

<svelte:head>
	<title>{queryToken ? `അംഗത്വ പരിശോധന: ${queryToken} | GigWorkers.Online` : (lang === 'ml' ? 'പൊതു അംഗത്വ പരിശോധന | GigWorkers.Online' : 'Public Member Verification | GigWorkers.Online')}</title>
</svelte:head>

{#if queryToken}
	<VerifyCardView token={queryToken} />
{:else}
	<!-- Sticky Header -->
	<header class="fixed top-0 left-0 right-0 w-full z-50 bg-white/95 backdrop-blur-md shadow-xs border-b border-slate-200/80">
		<div class="h-16 sm:h-20 max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 flex items-center justify-between gap-2">
			<a href="/" class="flex items-center gap-2 sm:gap-3 min-w-0 flex-shrink">
				<img
					src="/gigLogo.png"
					alt="Kerala State Gig and Platform Workers Union (CITU) Official Logo"
					class="w-9 h-9 sm:w-10 sm:h-10 rounded-full object-contain drop-shadow-sm shrink-0"
					onerror={(e) => {
						(e.currentTarget as HTMLImageElement).src = '/images/gigLogo.png';
					}}
				/>
				<div class="flex flex-col min-w-0">
					<div class="flex items-center gap-1.5 sm:gap-2">
						<span class="text-sm sm:text-base tracking-tight text-slate-900 uppercase font-black truncate">GigWorkers.Online</span>
						<span class="hidden sm:inline-block px-2 py-0.5 rounded-full bg-red-100 text-red-800 text-[10px] uppercase font-bold">
							Trade Union
						</span>
					</div>
					<span class="text-[10px] sm:text-xs text-slate-500 font-medium truncate">
						{lang === 'ml' ? 'അംഗത്വ പരിശോധന / Member Verification' : 'Public Member Verification'}
					</span>
				</div>
			</a>

			<div class="flex items-center gap-2 sm:gap-3 flex-shrink-0">
				<div class="inline-flex items-center bg-slate-100 border border-slate-200 rounded-full p-0.5 sm:p-1 shadow-inner">
					<button 
						type="button" 
						onclick={() => lang = 'ml'}
						class={`px-2 sm:px-3 py-1 rounded-full text-[11px] sm:text-xs font-bold transition-all ${lang === 'ml' ? 'bg-primary text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'}`}
					>
						മലയാളം
					</button>
					<button 
						type="button" 
						onclick={() => lang = 'en'}
						class={`px-2 sm:px-3 py-1 rounded-full text-[11px] sm:text-xs font-bold transition-all ${lang === 'en' ? 'bg-primary text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'}`}
					>
						EN
					</button>
				</div>

				<a href="/" class="hidden sm:inline-flex text-xs font-bold text-slate-600 hover:text-primary transition">
					Home
				</a>
			</div>
		</div>
	</header>

	<main class="w-full pt-28 hero-gradient-mesh min-h-[calc(100vh-80px)] flex flex-col items-center px-4">
		<div class="max-w-lg w-full card-gloss rounded-3xl shadow-2xl border border-slate-200/90 p-6 sm:p-9 text-center">
			<div class="w-16 h-16 rounded-2xl bg-red-100 text-primary flex items-center justify-center mx-auto mb-4 shadow-sm">
				<Icon name="qr_code_scanner" class="text-3xl" />
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
					<Icon name="badge" class="absolute left-3.5 text-slate-400 text-[20px]" />
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
					<Icon name="verified" class="text-[18px]" />
					<span>{lang === 'ml' ? 'പരിശോധിക്കുക' : 'Verify Credentials'}</span>
				</button>
			</form>

			<!-- Sample Verification Quick Links -->
			<div class="mt-6 pt-5 border-t border-surface-variant text-left">
				<span class="text-xs text-secondary font-semibold block mb-2">
					{lang === 'ml' ? 'സാമ്പിൾ ഐഡികൾ പരിശോധിക്കുക:' : 'Sample Active Records:'}
				</span>
				<div class="flex flex-wrap gap-2">
					<a href="/verify?token=KLTVC000009" class="px-3 py-1 rounded bg-surface-container hover:bg-surface-container-high text-xs font-mono font-semibold text-primary">
						KLTVC000009 (Zomato)
					</a>
					<a href="/verify?token=KLERN000142" class="px-3 py-1 rounded bg-surface-container hover:bg-surface-container-high text-xs font-mono font-semibold text-primary">
						KLERN000142 (Uber)
					</a>
					<a href="/verify?token=KLKZD000219" class="px-3 py-1 rounded bg-surface-container hover:bg-surface-container-high text-xs font-mono font-semibold text-primary">
						KLKZD000219 (Swiggy)
					</a>
				</div>
			</div>

			<!-- DPDP Notice -->
			<div class="mt-6 p-3 rounded-lg bg-surface-container-low text-[11px] text-secondary text-left flex items-start gap-2 border border-surface-variant">
				<Icon name="privacy_tip" class="text-[15px] shrink-0 text-secondary mt-0.5" />
				<span><strong>DPDP Act 2023 Compliant:</strong> Zero personal contact details disclosed. Public verification validates union accreditation only.</span>
			</div>
		</div>
	</main>

	<footer class="w-full bg-surface-container-lowest border-t border-surface-variant py-6 mt-12 text-center text-xs text-secondary flex flex-col items-center justify-center gap-2">
		<div class="flex items-center gap-2">
			<img src="/gigLogo.png" alt="CITU Gig Workers Official Logo" class="w-4 h-4 object-contain" />
			<span>GigWorkers.Online · Kerala Gig &amp; Platform Workers Union (CITU)</span>
		</div>
		<div class="text-[11px] text-secondary">
			Reg. No: <strong>Tu19965</strong> · E Balananda Smaraka Office, CITU State Committee Office, Mele Thampanoor, Thampanoor P.O. · Ph: <a href="tel:9846063666" class="hover:underline text-primary font-semibold">9846063666</a>, <a href="tel:9447695655" class="hover:underline text-primary font-semibold">9447695655</a>
		</div>
	</footer>
{/if}
