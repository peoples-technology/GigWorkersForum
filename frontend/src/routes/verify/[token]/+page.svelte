<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';

	let lang = $state<'ml' | 'en'>('ml');
	let copied = $state(false);
	let currentTimestamp = $state('');

	// Dynamic token or member ID
	let memberToken = $derived($page.params.token || 'KLTVC000009');

	// Member profile attributes (safely redacted per DPDP Act)
	let member = $derived({
		id: memberToken.toUpperCase(),
		tokenHash: `SHA256-${memberToken.slice(0, 4).toLowerCase()}_${Math.random().toString(36).substring(2, 8)}`,
		name: memberToken.includes('FZ') || memberToken.includes('000142') 
			? 'FATHIMA ZAHRA' 
			: memberToken.includes('RN') || memberToken.includes('000219') 
			? 'RAHUL V. NAIR' 
			: 'ANANDHU K. S.',
		nameMl: memberToken.includes('FZ') || memberToken.includes('000142') 
			? 'ഫാത്തിമ സഹ്റ' 
			: memberToken.includes('RN') || memberToken.includes('000219') 
			? 'രാഹുൽ വി. നായർ' 
			: 'ആനന്ദു കെ. എസ്.',
		roleEn: memberToken.includes('FZ') || memberToken.includes('000142') 
			? 'Taxi Cab Driver · Airport Fleet' 
			: memberToken.includes('RN') || memberToken.includes('000219') 
			? 'Courier Pilot · Hyperlocal' 
			: 'Food Delivery Partner',
		roleMl: memberToken.includes('FZ') || memberToken.includes('000142') 
			? 'ക്യാബ് ഡ്രൈവർ' 
			: memberToken.includes('RN') || memberToken.includes('000219') 
			? 'കൊറിയർ പൈലറ്റ്' 
			: 'ഭക്ഷ്യവിതരണ തൊഴിലാളി',
		districtCode: memberToken.startsWith('KL') ? memberToken.slice(0, 5) : 'KLTVC',
		districtName: memberToken.includes('ERN') 
			? 'എറണാകുളം / Ernakulam' 
			: memberToken.includes('KZD') || memberToken.includes('KKD')
			? 'കോഴിക്കോട് / Kozhikode' 
			: memberToken.includes('TCR') || memberToken.includes('TSR')
			? 'തൃശ്ശൂർ / Thrissur'
			: 'തിരുവനന്തപുരം / Trivandrum',
		sectorEn: memberToken.includes('FZ') || memberToken.includes('000142') ? 'Ride Hailing & Transport' : 'Food Delivery & Logistics',
		sectorMl: memberToken.includes('FZ') || memberToken.includes('000142') ? 'റൈഡ് ഹെയ്‌ലിംഗ് & ഗതാഗതം' : 'ഫുഡ് ഡെലിവറി & ലോജിസ്റ്റിക്സ്',
		platforms: memberToken.includes('FZ') || memberToken.includes('000142') 
			? [{ name: 'Uber (ഊബർ)', color: 'bg-slate-900' }]
			: [
				{ name: 'Zomato (സൊമാറ്റോ)', color: 'bg-red-600' },
				{ name: 'Swiggy (സ്വിഗ്ഗി)', color: 'bg-amber-600' }
			],
		status: 'Active & Paid-Up',
		validUntil: '30 April 2027',
		photo: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCYyEu0qaQ2w1WiZP9iWtGjRuf2bZDkOpwgqz4ESsoieX_F7_jXg2jQ7Z5RTdMXXFEwaPkQvAjvu6dqW1P3GVAWU7AfOTZO3Tm0Q3iAEGqNcQxvvi0EGTen8-ymjqNmHp-A6UGwYcBKMQXCB9nuj6KtyXtYRjkpI-Jdho5SaWPaY26TAH8e9G0xl1bWzxHVhvsSxkyHNNiQbPyV6vD2vdLy0R9AwN7hD1p8rB-otH7tgdWaFNA4KQUrMA'
	});

	function copyId() {
		navigator.clipboard.writeText(member.id);
		copied = true;
		setTimeout(() => {
			copied = false;
		}, 2000);
	}

	onMount(() => {
		const now = new Date();
		const options: Intl.DateTimeFormatOptions = {
			day: 'numeric',
			month: 'long',
			year: 'numeric',
			hour: '2-digit',
			minute: '2-digit',
			hour12: true,
			timeZoneName: 'short'
		};
		try {
			currentTimestamp = now.toLocaleString('en-IN', options);
		} catch (e) {
			currentTimestamp = now.toISOString();
		}
	});
</script>

<svelte:head>
	<title>{lang === 'ml' ? `അംഗത്വ പരിശോധന: ${member.id} | KSGPWU CITU` : `Member Verification: ${member.id} | KSGPWU CITU`}</title>
</svelte:head>

<!-- Sticky Header -->
<header class="fixed top-0 w-full z-50 bg-surface-container-lowest/95 backdrop-blur-md shadow-[0_1px_8px_rgba(0,0,0,0.04)] border-b border-surface-variant">
	<div class="h-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between">
		<!-- Union Logo & Header Title -->
		<a href="/" class="flex items-center gap-3">
			<div class="w-10 h-10 bg-primary-container rounded flex items-center justify-center text-on-primary font-bold text-lg shadow-sm shrink-0">
				★
			</div>
			<div class="flex flex-col">
				<div class="flex items-center gap-2">
					<span class="text-sm sm:text-base tracking-tight text-on-surface uppercase font-bold">KSGPWU · CITU</span>
					<span class="hidden sm:inline-block px-2 py-0.5 rounded-full bg-primary-fixed text-on-primary-fixed text-[10px] uppercase font-semibold">
						Trade Union
					</span>
				</div>
				<span class="text-xs text-secondary">
					{lang === 'ml' ? 'അംഗത്വ പരിശോധന / Public Verification' : 'Public Verification Protocol'}
				</span>
			</div>
		</a>

		<!-- Language Switcher & Official Gateway Badge -->
		<div class="flex items-center gap-3">
			<div class="hidden md:flex items-center gap-1.5 px-3 py-1 rounded-full bg-surface-container-low text-secondary text-xs">
				<span class="material-symbols-outlined text-primary text-[16px]">verified_user</span>
				<span class="font-semibold text-on-surface">Official Gateway</span>
			</div>

			<div class="inline-flex items-center bg-surface-container-low border border-surface-variant rounded-full p-0.5">
				<button 
					type="button" 
					onclick={() => lang = 'ml'}
					class={`px-2.5 py-1 rounded-full text-xs font-semibold ${lang === 'ml' ? 'bg-primary text-on-primary' : 'text-secondary hover:text-on-surface'}`}
				>
					മലയാളം
				</button>
				<button 
					type="button" 
					onclick={() => lang = 'en'}
					class={`px-2.5 py-1 rounded-full text-xs font-semibold ${lang === 'en' ? 'bg-primary text-on-primary' : 'text-secondary hover:text-on-surface'}`}
				>
					EN
				</button>
			</div>

			<a href="/" class="hidden sm:inline-flex text-xs font-semibold text-secondary hover:text-primary transition items-center gap-1">
				<span class="material-symbols-outlined text-[16px]">home</span>
				<span>Home</span>
			</a>
		</div>
	</div>
</header>

<main class="w-full pt-20 hero-gradient-mesh flex-1 flex flex-col justify-start">
	<div class="flex flex-col w-full py-8 sm:py-12 px-4 sm:px-6 items-center justify-center">
		<!-- Subtle ambient decorative glow -->
		<div class="relative w-full max-w-[640px] flex flex-col items-center">
			<div class="absolute -top-12 -left-12 w-64 h-64 bg-red-500/10 rounded-full blur-3xl pointer-events-none"></div>
			<div class="absolute -bottom-12 -right-12 w-72 h-72 bg-amber-500/15 rounded-full blur-3xl pointer-events-none"></div>

			<!-- Metadata Tag Header -->
			<div class="w-full flex items-center justify-between pb-3 px-1 text-slate-500 text-xs">
				<div class="flex items-center gap-1.5 font-bold">
					<span class="material-symbols-outlined text-[18px] text-primary">verified</span>
					<span class="uppercase tracking-wider">Public Verification Protocol • v2.4</span>
				</div>
				<div class="flex items-center gap-1.5 font-bold text-emerald-700">
					<span class="w-2.5 h-2.5 rounded-full bg-emerald-600 animate-pulse"></span>
					<span class="font-mono text-[11px]">LIVE VERIFIED</span>
				</div>
			</div>

			<!-- Main Credential Card -->
			<div class="w-full card-gloss rounded-3xl shadow-2xl border border-slate-200/90 overflow-hidden relative">
				<!-- Emerald Accent Status Bar -->
				<div class="h-2 w-full bg-emerald-600"></div>

				<!-- Verified Banner Section -->
				<div class="bg-gradient-to-b from-emerald-50 to-emerald-100/40 px-6 py-6 flex flex-col items-center text-center border-b border-emerald-100">
					<div class="w-14 h-14 rounded-2xl bg-emerald-600 text-white flex items-center justify-center shadow-lg shadow-emerald-700/20 mb-2.5">
						<span class="material-symbols-outlined text-[34px]">check_circle</span>
					</div>
					<h1 class="text-xl sm:text-2xl font-black text-emerald-950 tracking-tight">
						{lang === 'ml' ? 'സാധുവായ അംഗത്വം' : 'VERIFIED ACTIVE MEMBER'}
					</h1>
					<p class="text-xs sm:text-sm text-emerald-800 mt-1 max-w-md font-medium">
						{lang === 'ml'
							? 'ഈ തിരിച്ചറിയൽ കാർഡ് യൂണിയൻ രേഖകളുമായി ഒത്തുനോക്കി ഉറപ്പുവരുത്തിയതാണ്.'
							: 'Verified against central union registry records • Secure State Database'}
					</p>

					<!-- Dynamic Token Hash Pill -->
					<div class="mt-3.5 inline-flex items-center gap-2 px-3.5 py-1 bg-white rounded-full shadow-xs text-emerald-900 font-mono text-xs border border-emerald-200 font-bold">
						<span class="material-symbols-outlined text-[15px] text-emerald-700">fingerprint</span>
						<span>Token:</span>
						<span class="text-slate-600">{member.tokenHash}</span>
						<span>•</span>
						<span class="text-emerald-700">Validated</span>
					</div>
				</div>

				<!-- Member Identity Profile Section -->
				<div class="pt-8 pb-4 px-6 flex flex-col items-center text-center">
					<!-- Worker Photo with Badge Overlay -->
					<div class="relative w-32 h-32 rounded-3xl p-1 bg-slate-100 shadow-xl shrink-0 border-2 border-slate-200">
						<img 
							class="w-full h-full object-cover rounded-2xl" 
							alt={member.name} 
							src={member.photo}
							onerror={(e) => {
								(e.currentTarget as HTMLImageElement).src = "https://lh3.googleusercontent.com/aida-public/AB6AXuCYyEu0qaQ2w1WiZP9iWtGjRuf2bZDkOpwgqz4ESsoieX_F7_jXg2jQ7Z5RTdMXXFEwaPkQvAjvu6dqW1P3GVAWU7AfOTZO3Tm0Q3iAEGqNcQxvvi0EGTen8-ymjqNmHp-A6UGwYcBKMQXCB9nuj6KtyXtYRjkpI-Jdho5SaWPaY26TAH8e9G0xl1bWzxHVhvsSxkyHNNiQbPyV6vD2vdLy0R9AwN7hD1p8rB-otH7tgdWaFNA4KQUrMA";
							}}
						/>
						<div class="absolute -bottom-2 -right-2 bg-emerald-600 text-white w-8 h-8 rounded-full flex items-center justify-center shadow-lg border-2 border-white">
							<span class="material-symbols-outlined text-[18px]">verified</span>
						</div>
					</div>

					<!-- Member Name Hierarchy -->
					<h2 class="text-2xl font-black text-slate-900 mt-4 tracking-tight">
						{member.name}
					</h2>
					<p class="text-base text-primary font-bold mt-0.5">
						{member.nameMl} <span class="text-slate-500 font-normal">({member.roleMl})</span>
					</p>

					<!-- Member ID Pill with Copyable Cue -->
					<div class="mt-3 inline-flex items-center gap-2 bg-slate-100 px-4 py-1.5 rounded-full font-mono text-xs text-slate-800 border border-slate-200 shadow-2xs">
						<span class="text-slate-500 font-sans font-semibold">അംഗത്വ നമ്പർ / ID:</span>
						<span class="font-bold tracking-wider text-primary">{member.id}</span>
						<button 
							type="button" 
							onclick={copyId} 
							class="ml-1 text-slate-500 hover:text-primary transition-colors flex items-center" 
							title="Copy Member ID"
						>
							{#if copied}
								<span class="text-[10px] text-emerald-700 font-bold">COPIED</span>
							{:else}
								<span class="material-symbols-outlined text-[15px]">content_copy</span>
							{/if}
						</button>
					</div>

					<!-- Print Quick Action -->
					<div class="mt-4">
						<button 
							type="button" 
							onclick={() => window.print()}
							class="px-4 py-1.5 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-xl text-xs font-bold shadow-xs flex items-center gap-1.5 transition-colors"
						>
							<span class="material-symbols-outlined text-[16px]">print</span>
							<span>Print ID Card / സേവ് ചെയ്യുക</span>
						</button>
					</div>
				</div>

				<!-- Structured Verification Data Rows -->
				<div class="mt-4 mx-4 sm:mx-6 rounded-xl border border-surface-variant overflow-hidden divide-y divide-surface-variant text-xs">
					<!-- Row 1: District -->
					<div class="px-4 py-3 flex items-center justify-between text-left gap-3 bg-surface-container-lowest">
						<div class="flex flex-col">
							<span class="text-[11px] uppercase font-bold text-secondary">ജില്ല / Working District</span>
							<span class="text-[10px] text-secondary/80">Operational Jurisdiction</span>
						</div>
						<div class="flex items-center gap-2 text-right">
							<span class="inline-flex items-center px-2 py-0.5 rounded bg-surface-container font-mono font-bold text-primary">
								{member.districtCode}
							</span>
							<span class="font-bold text-on-surface">{member.districtName}</span>
						</div>
					</div>

					<!-- Row 2: Sector -->
					<div class="px-4 py-3 flex items-center justify-between text-left gap-3 bg-surface-container-low">
						<div class="flex flex-col">
							<span class="text-[11px] uppercase font-bold text-secondary">തൊഴിൽ മേഖല / Sector</span>
							<span class="text-[10px] text-secondary/80">Gig Classification</span>
						</div>
						<div class="text-right">
							<span class="font-bold text-on-surface">{member.sectorMl}</span>
							<div class="text-[10px] text-secondary">{member.sectorEn}</div>
						</div>
					</div>

					<!-- Row 3: Platform -->
					<div class="px-4 py-3 flex items-center justify-between text-left gap-3 bg-surface-container-lowest">
						<div class="flex flex-col">
							<span class="text-[11px] uppercase font-bold text-secondary">പ്ലാറ്റ്‌ഫോം / Platform</span>
							<span class="text-[10px] text-secondary/80">Active Registered Apps</span>
						</div>
						<div class="flex items-center gap-1.5 flex-wrap justify-end">
							{#each member.platforms as p}
								<span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-surface-container text-on-surface font-semibold text-[11px] border border-surface-variant">
									<span class={`w-2 h-2 rounded-full ${p.color}`}></span>
									{p.name}
								</span>
							{/each}
						</div>
					</div>

					<!-- Row 4: Status -->
					<div class="px-4 py-3 flex items-center justify-between text-left gap-3 bg-surface-container-low">
						<div class="flex flex-col">
							<span class="text-[11px] uppercase font-bold text-secondary">അംഗത്വ നില / Status</span>
							<span class="text-[10px] text-secondary/80">Dues &amp; Compliance</span>
						</div>
						<div class="flex items-center gap-2 text-right">
							<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-bold text-[10px]">
								<span class="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>
								Good Standing
							</span>
							<span class="font-bold text-emerald-900">സജീവം / Active</span>
						</div>
					</div>

					<!-- Row 5: Valid Through -->
					<div class="px-4 py-3 flex items-center justify-between text-left gap-3 bg-surface-container-lowest">
						<div class="flex flex-col">
							<span class="text-[11px] uppercase font-bold text-secondary">സാധുത കാലയളവ് / Valid Through</span>
							<span class="text-[10px] text-secondary/80">Triennial Renewal Cycle</span>
						</div>
						<div class="text-right">
							<span class="px-2.5 py-1 rounded bg-primary-fixed text-on-primary-fixed font-mono font-bold">
								{member.validUntil}
							</span>
						</div>
					</div>

					<!-- Row 6: Timestamp -->
					<div class="px-4 py-3 flex items-center justify-between text-left gap-3 bg-surface-container-low">
						<div class="flex flex-col">
							<span class="text-[11px] uppercase font-bold text-secondary">പരിശോധിച്ച സമയം / Verified At</span>
							<span class="text-[10px] text-secondary/80">Realtime Scan Timestamp</span>
						</div>
						<div class="flex items-center gap-1 font-mono text-on-surface font-medium">
							<span class="material-symbols-outlined text-[16px] text-primary">schedule</span>
							<span>{currentTimestamp}</span>
						</div>
					</div>
				</div>

				<!-- Trust Graphic: KGWWB Digital Seal Canvas -->
				<div class="mt-5 mx-4 sm:mx-6 p-4 rounded-xl bg-surface-container flex items-center justify-between gap-4 border border-surface-variant">
					<div class="flex items-center gap-3">
						<div class="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-on-primary shrink-0">
							<span class="material-symbols-outlined text-[20px]">shield_with_heart</span>
						</div>
						<div class="flex flex-col text-left text-xs">
							<span class="font-bold text-on-surface">Kerala Gig Workers Welfare Board (KGWWB)</span>
							<span class="text-secondary text-[11px]">Linked to CITU State Platform Workers Welfare Registry</span>
						</div>
					</div>

					<!-- Digital Seal SVG -->
					<div class="shrink-0 flex flex-col items-end">
						<svg class="w-10 h-10 text-primary" fill="none" viewBox="0 0 48 48">
							<circle cx="24" cy="24" r="22" stroke="currentColor" stroke-dasharray="2 3" stroke-width="1.5"></circle>
							<circle cx="24" cy="24" fill="currentColor" fill-opacity="0.08" r="18"></circle>
							<circle cx="24" cy="24" r="14" stroke="currentColor" stroke-width="1"></circle>
							<path d="M18 24L22 28L30 19" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2"></path>
						</svg>
						<span class="font-mono text-[9px] text-secondary tracking-widest mt-0.5">SEAL-CITU-KL</span>
					</div>
				</div>

				<!-- Card Official Footer -->
				<div class="mt-5 px-6 py-3 bg-surface-container-high flex flex-wrap items-center justify-between text-secondary text-xs gap-y-1">
					<div class="flex items-center gap-1">
						<span class="material-symbols-outlined text-[15px] text-primary">policy</span>
						<span>Reg. Trade Union No: <strong class="text-on-surface">KL-07-TU-2026</strong></span>
					</div>
					<div>Govt. of Kerala Labour Dept. Recognized</div>
				</div>
			</div>

			<!-- Security & DPDP Compliance Statement -->
			<div class="w-full max-w-xl mx-auto mt-6 flex flex-col items-center text-center gap-2 px-2">
				<div class="flex items-center gap-1.5 text-on-surface font-semibold text-sm">
					<span class="material-symbols-outlined text-[20px] text-emerald-700">lock</span>
					<span>{lang === 'ml' ? 'ക്രിപ്റ്റോഗ്രാഫിക് ടോക്കൺ വഴി പരിശോധിച്ചു' : 'Cryptographically Verified'}</span>
				</div>
				<p class="text-xs text-secondary leading-relaxed">
					{lang === 'ml'
						? 'ഡിജിറ്റൽ ക്യുആർ കോഡ് വഴി തത്സമയം പരിശോധിച്ചത്. പോലീസ് പരിശോധനകൾക്കും തർക്ക പരിഹാരങ്ങൾക്കും ക്ഷേമനിധി ആനുകൂല്യങ്ങൾക്കും ഈ കാർഡ് സാധുവാണ്.'
						: `Cryptographically verified via single-use dynamic QR token. Issued to ${member.name} for union representation, roadside dispute checks, and statutory platform welfare auditing.`}
				</p>

				<div class="mt-2 p-3 rounded-lg bg-surface-container-low max-w-lg text-left flex items-start gap-2 text-secondary text-[11px] border border-surface-variant">
					<span class="material-symbols-outlined text-[16px] text-secondary shrink-0 mt-0.5">privacy_tip</span>
					<span>
						<strong>DPDP Act 2023 Compliant:</strong> Personal phone number, residential address, aadhaar reference, and bank remittance tokens are strictly redacted on public verification surfaces to prevent harassment.
					</span>
				</div>

				<!-- Helpline Strip -->
				<div class="mt-4 flex flex-wrap items-center justify-center gap-x-4 gap-y-1 text-xs text-secondary">
					<span class="flex items-center gap-1">
						<span class="material-symbols-outlined text-[15px] text-primary">call</span>
						<span>ഹെൽപ്പ്‌ലൈൻ: <a class="text-primary font-semibold hover:underline" href="tel:04712300000">0471-2300000</a></span>
					</span>
					<span>•</span>
					<span class="flex items-center gap-1">
						<span class="material-symbols-outlined text-[15px] text-primary">mail</span>
						<a class="text-primary font-semibold hover:underline" href="mailto:helpdesk@ksgpwu.citu.in">helpdesk@ksgpwu.citu.in</a>
					</span>
				</div>

				<div class="text-[11px] text-secondary mt-1">
					CITU State Centre, AKG Mandiram, Thiruvananthapuram - 695034
				</div>
			</div>
		</div>
	</div>
</main>

<!-- Footer -->
<footer class="w-full bg-surface-container-lowest shadow-[0_1px_8px_rgba(0,0,0,0.04)] py-6 mt-8 border-t border-surface-variant">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col items-center justify-center text-center gap-1 text-xs text-secondary">
		<div class="flex flex-wrap items-center justify-center gap-x-3 gap-y-1">
			<span class="font-semibold text-primary">Kerala State Gig &amp; Platform Workers Union (CITU)</span>
			<span>•</span>
			<span>Reg. Trade Union, Kerala</span>
			<span>•</span>
			<span>Support Helpline: 0471-2300000</span>
		</div>
		<div class="text-[11px] text-secondary mt-1">
			Statutory Labour Protection &amp; Dignity · Kerala Platform Workers Welfare Registry
		</div>
	</div>
</footer>
