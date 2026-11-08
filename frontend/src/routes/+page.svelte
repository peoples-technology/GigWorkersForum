<script lang="ts">
	import { onMount } from 'svelte';

	let lang = $state<'ml' | 'en'>('ml');
	let mobileMenuOpen = $state(false);

	// Quick Access Card Download State
	let accessMode = $state<'id' | 'otp'>('id'); // 'id' = Enter Membership ID (Active), 'otp' = Mobile OTP (Locked)
	let memberIdInput = $state('');
	let trackPhone = $state('');
	let otpSending = $state(false);
	let otpSent = $state(false);
	let statusMessage = $state('');
	let statusType = $state<'info' | 'error' | 'success'>('info');
	let matchedMemberId = $state('');

	onMount(() => {
		// Background sync of locally registered members with photo to backend API
		try {
			const regStr = localStorage.getItem('ksgpwu_members_registry');
			if (regStr) {
				const reg = JSON.parse(regStr);
				for (const key of Object.keys(reg)) {
					const item = reg[key];
					if (item && item.photo && typeof item.photo === 'string' && item.photo.startsWith('data:image')) {
						fetch('/api/cards/sync-member', {
							method: 'POST',
							headers: { 'Content-Type': 'application/json' },
							body: JSON.stringify({
								id: item.id || key,
								name: item.name || 'CITU MEMBER',
								name_ml: item.nameMl || item.name || '',
								district_code: item.districtCode || 'KLTVC',
								district_name: item.districtNameEn || 'Thiruvananthapuram',
								primary_sector: item.primarySector || 'Food Delivery & Hyperlocal Logistics',
								primary_platform: item.primaryPlatform || 'Swiggy',
								vehicle_number: item.vehicleNumber || '',
								status: item.status || 'Active & Paid-Up',
								valid_until: item.validUntil || '31 October 2027',
								photo: item.photo
							})
						}).catch(() => {});
					}
				}
			}
		} catch (e) {}
	});

	function toggleLang(newLang: 'ml' | 'en') {
		lang = newLang;
	}

	function handleLookupMemberId() {
		const rawInput = memberIdInput.trim();
		if (!rawInput) {
			statusType = 'error';
			statusMessage = lang === 'ml' 
				? 'ദയവായി നിങ്ങളുടെ അംഗത്വ നമ്പർ നൽകുക (ഉദാ: KL-TVC-2026-3103).' 
				: 'Please enter your Membership ID (e.g. KL-TVC-2026-3103).';
			return;
		}

		// Check if user entered a 10-digit mobile number in the ID box
		const cleanDigits = rawInput.replace(/\D/g, '');
		if (cleanDigits.length === 10 || (cleanDigits.length === 12 && cleanDigits.startsWith('91'))) {
			const phone10 = cleanDigits.length === 12 ? cleanDigits.slice(2) : cleanDigits;
			try {
				const regStr = localStorage.getItem('ksgpwu_members_registry');
				if (regStr) {
					const reg = JSON.parse(regStr);
					if (reg[phone10]?.id) {
						window.location.href = `/verify?token=${encodeURIComponent(reg[phone10].id)}`;
						return;
					}
					for (const k in reg) {
						const m = reg[k];
						const mPhone = (m.mobile || m.phone || '').replace(/\D/g, '');
						if (mPhone === phone10) {
							const idToUse = m.id || m.memberId || k;
							window.location.href = `/verify?token=${encodeURIComponent(idToUse)}`;
							return;
						}
					}
				}
				const directStr = localStorage.getItem(`member_${phone10}`);
				if (directStr) {
					const d = JSON.parse(directStr);
					if (d?.id) {
						window.location.href = `/verify?token=${encodeURIComponent(d.id)}`;
						return;
					}
				}
			} catch (e) {}
		}

		// Navigate directly to verify page with token
		const cleanId = rawInput.toUpperCase();
		window.location.href = `/verify?token=${encodeURIComponent(cleanId)}`;
	}

	function handleSendOtp() {
		// Locked feature notification
		statusType = 'info';
		statusMessage = lang === 'ml'
			? '🔒 മൊബൈൽ ഒടിപി ഫീച്ചർ താൽക്കാലികമായി ലോക്ക് ചെയ്തിരിക്കുന്നു. കാർഡ് ഡൗൺലോഡ് ചെയ്യാൻ "Option 1: അംഗത്വ നമ്പർ" ഉപയോഗിക്കുക.'
			: '🔒 Mobile OTP is currently locked for telecom gateway maintenance. Please use "Option 1: Membership ID" to download your card.';
	}
</script>

<svelte:head>
	<title>{lang === 'ml' ? 'GigWorkers.Online · കേരള ഗിഗ് & പ്ലാറ്റ്‌ഫോം വർക്കേഴ്സ് യൂണിയൻ' : 'GigWorkers.Online · Kerala Gig & Platform Workers Union'}</title>
</svelte:head>

<!-- Frosted Glass Sticky Header -->
<header class="fixed top-0 left-0 right-0 w-full z-50 bg-white/95 backdrop-blur-md border-b border-slate-200/80 shadow-xs transition-all">
	<div class="h-16 sm:h-20 max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 flex items-center justify-between gap-2 sm:gap-4">
		<!-- Union Logo & Title -->
		<a href="/" class="flex items-center gap-2 sm:gap-3.5 min-w-0 flex-shrink group">
			<img
				src="/gigLogo.png"
				alt="Kerala State Gig and Platform Workers Union (CITU) Official Logo"
				class="w-9 h-9 sm:w-11 sm:h-11 rounded-full object-contain drop-shadow-sm group-hover:scale-105 transition-transform flex-shrink-0"
				onerror={(e) => {
					(e.currentTarget as HTMLImageElement).src = '/images/gigLogo.png';
				}}
			/>
			<div class="flex flex-col min-w-0">
				<div class="flex items-center gap-1.5 sm:gap-2">
					<span class="font-extrabold text-sm sm:text-lg text-slate-900 tracking-tight group-hover:text-primary transition-colors truncate">
						GigWorkers<span class="text-primary">.Online</span>
					</span>
					<span class="hidden md:inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-100 text-red-800 border border-red-200 uppercase tracking-wide">
						Kerala
					</span>
				</div>
				<span class="text-[10px] sm:text-xs text-slate-500 uppercase tracking-wider font-medium truncate">
					{lang === 'ml' ? 'കേരള ഗിഗ് & പ്ലാറ്റ്‌ഫോം വർക്കേഴ്സ് യൂണിയൻ' : 'Kerala Gig & Platform Workers Union'}
				</span>
			</div>
		</a>

		<!-- Desktop Navigation -->
		<nav class="hidden lg:flex items-center gap-1 font-semibold text-sm">
			<a href="#quick-access-banner" class="px-3.5 py-2 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100/80 transition-all">
				{lang === 'ml' ? 'അംഗത്വം' : 'Membership'}
			</a>
			<a href="/register" class="px-4 py-2 rounded-lg bg-red-50 text-primary border border-red-200/80 hover:bg-red-100/70 transition-all font-bold">
				{lang === 'ml' ? 'രജിസ്ട്രേഷൻ' : 'Register'}
			</a>
			<a href="/verify" class="px-3.5 py-2 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100/80 transition-all">
				{lang === 'ml' ? 'ഐഡി പരിശോധന' : 'Verify ID'}
			</a>
		</nav>

		<!-- Right Action Strip: Language Toggle + Register CTA + Hamburger -->
		<div class="flex items-center gap-1.5 sm:gap-3 flex-shrink-0">
			<!-- Language Toggle Pill -->
			<div class="inline-flex items-center bg-slate-100/90 border border-slate-200 rounded-full p-0.5 sm:p-1 shadow-inner">
				<button 
					type="button" 
					onclick={() => toggleLang('ml')}
					class={`px-2 sm:px-3 py-1 rounded-full text-[11px] sm:text-xs font-bold transition-all ${lang === 'ml' ? 'bg-primary text-white shadow-sm' : 'text-slate-600 hover:text-slate-900'}`}
				>
					മലയാളം
				</button>
				<button 
					type="button" 
					onclick={() => toggleLang('en')}
					class={`px-2 sm:px-3 py-1 rounded-full text-[11px] sm:text-xs font-bold transition-all ${lang === 'en' ? 'bg-primary text-white shadow-sm' : 'text-slate-600 hover:text-slate-900'}`}
				>
					EN
				</button>
			</div>

			<!-- Quick Register CTA Button -->
			<a 
				href="/register" 
				class="hidden sm:inline-flex items-center gap-1.5 px-3.5 sm:px-4 py-2 sm:py-2.5 rounded-xl crimson-gradient-btn text-white text-xs font-bold tracking-wide shadow-md"
			>
				<span class="material-symbols-outlined text-[16px]">how_to_reg</span>
				<span>{lang === 'ml' ? 'അംഗമാകുക (₹100)' : 'Join Union (₹100)'}</span>
			</a>

			<!-- Mobile Hamburger Toggle -->
			<button 
				type="button" 
				onclick={() => mobileMenuOpen = !mobileMenuOpen}
				class="lg:hidden p-1.5 sm:p-2 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100 focus:outline-none"
				aria-label="Toggle menu"
			>
				<span class="material-symbols-outlined text-2xl">{mobileMenuOpen ? 'close' : 'menu'}</span>
			</button>
		</div>
	</div>

	<!-- Mobile Menu Drawer -->
	{#if mobileMenuOpen}
		<div class="lg:hidden bg-white border-b border-slate-200 px-4 py-3 space-y-2 shadow-lg animate-in slide-in-from-top-2">
			<a 
				href="#quick-access-banner" 
				onclick={() => mobileMenuOpen = false} 
				class="block px-3 py-2 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-100"
			>
				{lang === 'ml' ? 'അംഗത്വ കാർഡ് ഡൗൺലോഡ് ചെയ്യുക' : 'Download Membership Card'}
			</a>
			<a 
				href="/register" 
				onclick={() => mobileMenuOpen = false} 
				class="block px-3 py-2.5 rounded-lg text-sm font-bold text-primary bg-red-50 border border-red-200/80"
			>
				{lang === 'ml' ? 'പുതിയ രജിസ്ട്രേഷൻ · Register (₹100)' : 'Register Member (₹100)'}
			</a>
			<a 
				href="/verify" 
				onclick={() => mobileMenuOpen = false} 
				class="block px-3 py-2 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-100"
			>
				{lang === 'ml' ? 'ഐഡി പരിശോധന · Verify Member' : 'Public Verification'}
			</a>
		</div>
	{/if}
</header>

<main class="w-full pt-16 sm:pt-20 min-h-[calc(100vh-80px)] overflow-x-hidden">
	<div class="flex flex-col w-full">
		<!-- Top Statutory Notification Ticker -->
		<aside aria-label="Statutory Notice" class="w-full bg-[#990000] text-white border-b border-[#7d000d]">
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2.5 flex flex-wrap items-center justify-between gap-2 text-xs">
				<div class="flex items-center gap-2.5 min-w-0">
					<span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-white/15 text-white font-bold text-[10px] uppercase tracking-wider shadow-xs flex-shrink-0">
						<span class="text-amber-300">★</span>
						<span>CITU AFFILIATED</span>
					</span>
					<span class="truncate font-medium text-white/95 text-xs">
						{lang === 'ml' 
							? 'കേരള ഗിഗ് & പ്ലാറ്റ്‌ഫോം തൊഴിലാളി യൂണിയൻ - രജിസ്ട്രേഷൻ നമ്പർ: Tu19965' 
							: 'Kerala Gig & Platform Workers Union - Reg No: Tu19965'}
					</span>
				</div>
				<div class="hidden sm:flex items-center gap-4 text-white/90 font-medium text-xs">
					<a href="tel:9846063666" class="flex items-center gap-1.5 hover:text-white hover:underline transition">
						<span class="material-symbols-outlined text-[15px] text-amber-300">call</span>
						<span>Ph: 9846063666, 9447695655</span>
					</a>
					<span class="text-white/40">•</span>
					<span class="flex items-center gap-1.5">
						<span class="material-symbols-outlined text-[15px] text-blue-200">location_on</span>
						<span>{lang === 'ml' ? 'മേലെ തമ്പാനൂർ, തിരുവനന്തപുരം' : 'Mele Thampanoor, TVM'}</span>
					</span>
				</div>
			</div>
		</aside>

		<!-- Hero Section -->
		<section class="relative w-full overflow-hidden bg-zinc-950 min-h-[580px] lg:min-h-[640px] xl:min-h-[720px] 2xl:min-h-[760px] flex items-center">
			<!-- 1. Background Illustration: Desktop vs Mobile -->
			<!-- Desktop Artwork (lg and above) -->
			<div class="hidden lg:block absolute inset-0 w-full h-full select-none pointer-events-none overflow-hidden z-0">
				<img
					src="/images/HeroBgDesktop.webp"
					alt="Kerala gig and platform workers united across Kerala"
					class="absolute inset-0 h-full w-full object-cover object-right-bottom select-none"
					onerror={(e) => {
						(e.currentTarget as HTMLImageElement).src = "/HeroBgDesktop.webp";
					}}
				/>
				<!-- Subtle Warm Tint (Preserves Kerala/Union branding warmth) -->
				<div class="absolute inset-0 bg-[#821111]/15 mix-blend-multiply pointer-events-none"></div>
			</div>

			<!-- Mobile Artwork (below lg) -->
			<div class="lg:hidden absolute inset-0 w-full h-full select-none pointer-events-none overflow-hidden z-0">
				<img
					src="/images/heroMobileBgColorFul.webp"
					alt="Kerala gig and platform workers united across Kerala"
					class="absolute inset-0 h-full w-full object-cover object-top select-none"
					onerror={(e) => {
						(e.currentTarget as HTMLImageElement).src = "/heroMobileBgColorFul.webp";
					}}
				/>
			</div>

			<!-- 2. Responsive Vignette: Top-to-Bottom for Mobile, Left-to-Right for Desktop -->
			<!-- On mobile (default), darkens from top/middle to ensure text readability. Transitions to side vignette on lg screens. -->
			<div class="absolute inset-0 bg-gradient-to-b from-zinc-950/90 via-zinc-950/70 to-zinc-950/40 lg:bg-gradient-to-r lg:from-zinc-950/80 lg:via-zinc-950/40 lg:to-transparent pointer-events-none z-0"></div>

			<!-- 3. Architectural Grid (Scaled back for cleanliness) -->
			<div class="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:20px_20px] opacity-15 pointer-events-none z-0"></div>

			<!-- Content Wrapper -->
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full relative z-10 pt-8 pb-12 lg:py-16 xl:py-20">
				<div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">

					<!-- Left Column: Copy & Actions (Centered on Mobile, Left-aligned on Desktop) -->
					<div class="lg:col-span-7 xl:col-span-6 flex flex-col items-center text-center lg:items-start lg:text-left w-full max-w-xl mx-auto lg:mx-0">

						<!-- Top Pill Badge -->
						<div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-red-950/80 border border-red-800/50 text-red-200 text-xs font-semibold mb-4 backdrop-blur-md shadow-sm">
							<span class="tracking-wide uppercase text-[11px] sm:text-xs font-bold">KERALA GIG &amp; PLATFORM WORKERS UNION</span>
							<span class="text-red-400 text-[10px] font-normal">(CITU)</span>
							<!-- Hammer & Sickle -->
							<svg class="w-3.5 h-3.5 flex-shrink-0" viewBox="0 0 100 100" fill="currentColor" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
								<rect x="10" y="50" width="55" height="9" rx="3" transform="rotate(-45 37 54)"/>
								<rect x="2" y="12" width="30" height="16" rx="3" transform="rotate(-45 17 20)"/>
								<path d="M 55 70 A 28 28 0 1 1 83 42" stroke="currentColor" stroke-width="9" fill="none" stroke-linecap="round"/>
								<path d="M 78 36 L 90 30 L 87 44 Z"/>
							</svg>
						</div>

						<!-- Headline with High Contrast -->
						<h1 class={`text-3xl sm:text-4xl lg:text-[3.6rem] xl:text-[4rem] font-black text-white tracking-tight drop-shadow-md mb-3 ${lang === 'ml' ? 'leading-[1.45] sm:leading-[1.5]' : 'leading-tight'}`}>
							{#if lang === 'ml'}
								<span class="block" style="font-family: 'Anek Malayalam', sans-serif;">
									<span class="block">ഒറ്റക്കല്ല നാം,</span>
									<span class="block mt-2 sm:mt-3.5">ഒന്നാണ് നമ്മൾ</span>
								</span>
							{:else}
								<span class="block">
									We Are Not Alone,<br/>
									<span class="text-red-400 italic font-black">We Stand as One</span>
								</span>
							{/if}
						</h1>

						<!-- Descriptive Text with Clean Backdrop Container -->
						<p class={`mt-1 text-sm sm:text-base lg:text-lg text-zinc-200 font-medium max-w-md lg:max-w-xl drop-shadow ${lang === 'ml' ? 'leading-[2.1] sm:leading-[2.2] tracking-wide' : 'leading-relaxed'}`} style={lang === 'ml' ? "font-family: 'Anek Malayalam', sans-serif;" : ""}>
							{lang === 'ml'
								? 'കേരളത്തിലെ ഗിഗ് & പ്ലാറ്റ്ഫോം മേഖലയിൽ പണിയെടുക്കുന്നവർ തങ്ങളുടെ അവകാശ സംരക്ഷണത്തിനും അമിത ചൂഷണത്തിന് എതിരെയും ഒരുമിക്കുന്നു.'
								: 'Gig and platform workers across Kerala unite to defend their rights and stand against unfair exploitation.'}
						</p>

						<!-- Action Buttons -->
						<div class="mt-6 flex flex-col sm:flex-row gap-3 w-full max-w-xs sm:max-w-none justify-center lg:justify-start">
							<a
								href="/register"
								class="w-full sm:w-auto px-6 py-3 rounded-xl bg-red-700 hover:bg-red-600 text-white font-bold shadow-lg shadow-red-950/40 transition-all flex items-center justify-center gap-2.5 text-sm"
							>
								<span style="font-family: 'Anek Malayalam', sans-serif;">അംഗമാകുക</span>
								<span class="opacity-40">|</span>
								<span class="uppercase tracking-wider text-xs font-black">JOIN THE UNION</span>
								<span class="material-symbols-outlined text-[18px]">arrow_forward</span>
							</a>

							<a
								href="#quick-access-banner"
								class="w-full sm:w-auto px-6 py-3 rounded-xl bg-white/10 hover:bg-white/20 backdrop-blur-md text-white font-medium border border-white/20 transition-all flex items-center justify-center gap-2 text-sm shadow-sm"
							>
								<span class="material-symbols-outlined text-[18px] text-zinc-300">download</span>
								{#if lang === 'ml'}
									<span style="font-family: 'Anek Malayalam', sans-serif;">അംഗത്വ കാർഡ് ഡൗൺലോഡ് ചെയ്യുക</span>
								{:else}
									<span>Download Membership Card</span>
								{/if}
							</a>
						</div>

						<!-- Floating Stats Strip Matching Reference Mockup -->
						<div class="mt-8 grid grid-cols-3 gap-4 sm:gap-8 w-full max-w-md pt-4 border-t border-white/10">
							<div>
								<p class="text-2xl sm:text-3xl lg:text-4xl font-black text-white leading-none">14</p>
								<p class="text-[11px] sm:text-xs text-zinc-400 font-semibold mt-1.5 uppercase tracking-wider">
									{lang === 'ml' ? 'ജില്ലകൾ' : 'Districts'}
								</p>
							</div>
							<div>
								<p class="text-2xl sm:text-3xl lg:text-4xl font-black text-amber-400 leading-none">₹100</p>
								<p class="text-[11px] sm:text-xs text-zinc-400 font-semibold mt-1.5 uppercase tracking-wider">
									{lang === 'ml' ? 'രജിസ്ട്രേഷൻ ഫീസ്' : 'Registration Fee'}
								</p>
							</div>
							<div>
								<p class="text-2xl sm:text-3xl lg:text-4xl font-black text-emerald-400 leading-none">100%</p>
								<p class="text-[11px] sm:text-xs text-zinc-400 font-semibold mt-1.5 uppercase tracking-wider">
									{lang === 'ml' ? 'നിയമ സുരക്ഷ' : 'Legal Cover'}
								</p>
							</div>
						</div>
					</div>

					<!-- Desktop Spacer Column (Allows HeroBgDesktop.webp workers to shine through cleanly) -->
					<div class="hidden lg:block lg:col-span-5 xl:col-span-6 pointer-events-none"></div>

					<!-- Mobile Spacer (Showcases heroMobileBgColorFul.webp workers and slogan without overlap) -->
					<div class="lg:hidden w-full min-h-[260px] sm:min-h-[340px] pointer-events-none"></div>

				</div>
			</div>
		</section>

		<!-- Three Feature Highlights -->
		<section class="w-full py-16 bg-slate-50 border-y border-slate-200/80">
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
				<div class="flex flex-col md:flex-row md:items-end justify-between mb-10 gap-3">
					<div>
						<span class="text-primary text-xs uppercase tracking-wider font-extrabold flex items-center gap-1.5">
							<span class="w-2 h-2 rounded-full bg-primary"></span>
							{lang === 'ml' ? 'ഡിജിറ്റൽ ആനുകൂല്യങ്ങൾ' : 'Digital Protections'}
						</span>
						<h2 class="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight mt-1.5">
							{lang === 'ml' ? 'തൊഴിലാളി ക്ഷേമവും അംഗത്വ ആനുകൂല്യങ്ങളും' : 'Platform Protections & Member Services'}
						</h2>
					</div>
					<p class={`text-xs sm:text-sm text-slate-600 max-w-md ${lang === 'ml' ? 'leading-[1.9] sm:leading-[2.0]' : 'leading-relaxed'}`}>
						{lang === 'ml' 
							? 'കേരളത്തിലെ എല്ലാ ഡെലിവറി, ക്യാബ്, ഇ-കൊമേഴ്സ് ഗിഗ് തൊഴിലാളികൾക്കും വിരൽത്തുമ്പിൽ സഹായം.' 
							: 'Designed for frictionless operation in Kerala’s delivery, transport, and digital work sectors.'}
					</p>
				</div>

				<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
					<!-- Feature 1 -->
					<article class="card-gloss card-gloss-hover p-7 rounded-2xl flex flex-col justify-between relative overflow-hidden group">
						<div class="h-1 w-full bg-primary absolute top-0 left-0"></div>
						<div>
							<div class="w-14 h-14 rounded-2xl bg-red-100 text-primary flex items-center justify-center mb-5 shadow-xs group-hover:scale-105 transition-transform">
								<span class="material-symbols-outlined text-[30px]">phonelink_lock</span>
							</div>
							<h3 class="text-lg font-bold text-slate-900 mb-2.5">
								{lang === 'ml' ? 'സ്വയം രജിസ്ട്രേഷൻ' : 'Instant Registration'}
							</h3>
							<p class={`text-sm text-slate-600 ${lang === 'ml' ? 'leading-[2.05] sm:leading-[2.1]' : 'leading-relaxed'}`}>
								{lang === 'ml'
									? 'മൊബൈൽ ഒടിപി വഴി മിനിറ്റുകൾക്കുള്ളിൽ വേരിഫിക്കേഷൻ. സ്വിഗ്ഗി, സൊമാറ്റോ, ഊബർ, ഒല, ആമസോൺ തൊഴിലാളികൾക്ക് ലളിതമായ രജിസ്ട്രേഷൻ.'
									: 'Verified instantly via secure mobile SMS OTP. Enter your vehicle or delivery partner ID for automated activation across Zomato, Swiggy, Uber, Ola, and courier platforms.'}
							</p>
						</div>
						<div class="mt-6 pt-4 border-t border-slate-100 flex items-center gap-2 text-primary text-xs font-bold">
							<span>{lang === 'ml' ? '2 മിനിറ്റിനകം ആക്റ്റീവ്' : 'Active in 2 minutes'}</span>
							<span class="material-symbols-outlined text-[18px]">check_circle</span>
						</div>
					</article>

					<!-- Feature 2 -->
					<article class="card-gloss card-gloss-hover p-7 rounded-2xl flex flex-col justify-between relative overflow-hidden group">
						<div class="h-1 w-full bg-blue-600 absolute top-0 left-0"></div>
						<div>
							<div class="w-14 h-14 rounded-2xl bg-blue-100 text-blue-700 flex items-center justify-center mb-5 shadow-xs group-hover:scale-105 transition-transform">
								<span class="material-symbols-outlined text-[30px]">badge</span>
							</div>
							<h3 class="text-lg font-bold text-slate-900 mb-2.5">
								{lang === 'ml' ? 'ഡിജിറ്റൽ അംഗത്വ കാർഡ്' : 'Digital Membership ID Card'}
							</h3>
							<p class={`text-sm text-slate-600 ${lang === 'ml' ? 'leading-[2.05] sm:leading-[2.1]' : 'leading-relaxed'}`}>
								{lang === 'ml'
									? 'തത്സമയം ഡൗൺലോഡ് ചെയ്യാവുന്ന ക്രിപ്റ്റോഗ്രാഫിക് ക്യുആർ കോഡ് അടങ്ങിയ യൂണിയൻ ഡിജിറ്റൽ തിരിച്ചറിയൽ കാർഡ്.'
									: 'Instantly generate an authenticated digital union membership ID card carrying a dynamic cryptographically verified QR seal for roadside verification and labour claims.'}
							</p>
						</div>
						<div class="mt-6 pt-4 border-t border-slate-100 flex items-center gap-2 text-blue-700 text-xs font-bold">
							<span>{lang === 'ml' ? 'QR-സ്ഥിരീകരിച്ച ഐഡി' : 'Cryptographic QR Seal'}</span>
							<span class="material-symbols-outlined text-[18px]">qr_code_scanner</span>
						</div>
					</article>

					<!-- Feature 3 -->
					<article class="card-gloss card-gloss-hover p-7 rounded-2xl flex flex-col justify-between relative overflow-hidden group">
						<div class="h-1 w-full bg-amber-600 absolute top-0 left-0"></div>
						<div>
							<div class="w-14 h-14 rounded-2xl bg-amber-100 text-amber-800 flex items-center justify-center mb-5 shadow-xs group-hover:scale-105 transition-transform">
								<span class="material-symbols-outlined text-[30px]">support</span>
							</div>
							<h3 class="text-lg font-bold text-slate-900 mb-2.5">
								{lang === 'ml' ? 'സഹായം & പരാതി പരിഹാരം' : 'Helpline & Grievance'}
							</h3>
							<p class={`text-sm text-slate-600 ${lang === 'ml' ? 'leading-[2.05] sm:leading-[2.1]' : 'leading-relaxed'}`}>
								{lang === 'ml'
									? '14 ജില്ലകളിലും അന്യായമായ ഐഡി ബ്ലോക്കിംഗിനെതിരെ നിയമസഹായം, അപകട ഇൻഷുറൻസ് ക്ലെയിം സഹായം, ഒത്തുതീർപ്പ് സമിതികൾ.'
									: 'Direct access to all 14-district worker conciliation committees, legal aid desks for wrongful platform deactivation, and immediate accident assistance squads.'}
							</p>
						</div>
						<div class="mt-6 pt-4 border-t border-slate-100 flex items-center gap-2 text-amber-800 text-xs font-bold">
							<span>{lang === 'ml' ? '24/7 നിയമ സഹായം' : '24/7 Legal Assistance'}</span>
							<span class="material-symbols-outlined text-[18px]">call</span>
						</div>
					</article>
				</div>
			</div>
		</section>

		<!-- Member Quick Access Banner with Deep Gradient -->
		<section class="w-full py-12 sm:py-16 bg-white" id="quick-access-banner">
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
				<div class="bg-gradient-to-br from-slate-950 via-slate-900 to-red-950 text-white rounded-2xl sm:rounded-3xl p-5 sm:p-10 lg:p-12 border border-slate-800 shadow-2xl relative overflow-hidden">
					<!-- Ambient Glow Inside Card -->
					<div class="absolute -top-20 -right-20 w-80 h-80 bg-red-600/15 rounded-full blur-3xl pointer-events-none"></div>

					<div class="grid grid-cols-1 lg:grid-cols-12 gap-6 sm:gap-8 items-center relative z-10">
						<!-- Text Lockup -->
						<div class="lg:col-span-5">
							<div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-900/40 text-red-300 border border-red-500/30 text-[11px] sm:text-xs font-bold mb-3 sm:mb-4">
								<span class="material-symbols-outlined text-[15px] sm:text-[16px]">badge</span>
								<span>{lang === 'ml' ? 'നിലവിലുള്ള അംഗങ്ങൾക്കായി · Portal Access' : 'Existing Members · Quick Access'}</span>
							</div>
							<h3 class="text-xl sm:text-3xl font-black text-white">
								{lang === 'ml' ? 'അംഗത്വ കാർഡ് ഡൗൺലോഡ് ചെയ്യുക' : 'Download Membership Card'}
							</h3>
							<p class={`text-xs sm:text-sm text-slate-300 mt-2 sm:mt-2.5 max-w-lg ${lang === 'ml' ? 'leading-[2.05] sm:leading-[2.1]' : 'leading-relaxed'}`}>
								{#if accessMode === 'id'}
									{lang === 'ml'
										? 'നിങ്ങളുടെ ഔദ്യോഗിക അംഗത്വ നമ്പർ (ഉദാ: KL-TVC-2026-3103 അല്ലെങ്കിൽ KLTVC000009) നൽകി ഔദ്യോഗിക ഡിജിറ്റൽ കാർഡ് നേരിട്ട് ഡൗൺലോഡ് ചെയ്യുക.'
										: 'Enter your official Membership ID (e.g. KL-TVC-2026-3103 or KLTVC000009) to instantly view and download your verified union ID card.'}
								{:else}
									{lang === 'ml'
										? 'മൊബൈൽ ഒടിപി ഫീച്ചർ ടെലികോം ഡിഎൽടി (DLT) എസ്എംഎസ് സുരക്ഷാ പരിശോധനയിലാണ്. ഈ ഫീച്ചർ താൽക്കാലികമായി ലോക്ക് ചെയ്തിരിക്കുന്നു.'
										: 'Direct SMS OTP verification is undergoing telecom DLT gateway compliance provisioning. This feature is currently locked.'}
								{/if}
							</p>
						</div>

						<!-- Two Options Segmented Switcher & Forms -->
						<div class="lg:col-span-7 w-full flex flex-col gap-3">
							<!-- 2 Options Mode Selector -->
							<div class="flex items-center gap-2 p-1 bg-slate-900/90 rounded-xl border border-slate-700/80 w-full sm:w-auto self-start">
								<button
									type="button"
									onclick={() => { accessMode = 'id'; statusMessage = ''; }}
									class={`px-3 sm:px-4 py-2 rounded-lg text-xs font-bold transition flex items-center gap-1.5 ${accessMode === 'id' ? 'bg-primary text-white shadow-sm ring-1 ring-red-400/30' : 'text-slate-400 hover:text-white'}`}
								>
									<span class="material-symbols-outlined text-[16px]">badge</span>
									<span>{lang === 'ml' ? '1. അംഗത്വ നമ്പർ' : '1. Enter Membership ID'}</span>
								</button>
								<button
									type="button"
									onclick={() => { accessMode = 'otp'; statusMessage = ''; }}
									class={`px-3 sm:px-4 py-2 rounded-lg text-xs font-bold transition flex items-center gap-1.5 ${accessMode === 'otp' ? 'bg-amber-900/60 text-amber-200 border border-amber-600/40' : 'text-slate-400 hover:text-white'}`}
								>
									<span class="material-symbols-outlined text-[16px]">lock</span>
									<span>{lang === 'ml' ? '2. മൊബൈൽ OTP' : '2. Mobile OTP'}</span>
									<span class="text-[9px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 font-mono font-bold uppercase tracking-wider">Locked</span>
								</button>
							</div>

							<!-- OPTION 1: Enter Membership ID (Active) -->
							{#if accessMode === 'id'}
								<form class="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5 sm:gap-3 w-full" onsubmit={(e) => { e.preventDefault(); handleLookupMemberId(); }}>
									<div class="relative flex-1 flex items-center bg-white rounded-xl border border-slate-300 overflow-hidden shadow-sm focus-within:ring-2 focus-within:ring-primary focus-within:border-primary w-full">
										<span class="bg-slate-100 px-3 py-2.5 sm:px-3.5 sm:py-3 text-xs sm:text-sm text-slate-700 border-r border-slate-300 flex items-center font-mono font-bold flex-shrink-0">
											ID
										</span>
										<input 
											bind:value={memberIdInput}
											class="w-full min-w-0 px-3 py-2.5 sm:px-3.5 sm:py-3 text-sm text-slate-900 placeholder:text-slate-400 bg-transparent focus:outline-none font-mono font-bold uppercase tracking-wide" 
											id="member-id-input" 
											placeholder={lang === 'ml' ? 'അംഗത്വ നമ്പർ (ഉദാ: KL-TVC-2026-3103)' : 'Membership ID (e.g. KL-TVC-2026-3103)'} 
											type="text"
											autocomplete="off"
										/>
									</div>
									<button 
										class="px-6 sm:px-7 py-3 sm:py-3.5 rounded-xl crimson-gradient-btn text-white text-sm font-bold whitespace-nowrap flex items-center justify-center gap-2 shadow-lg flex-shrink-0 transition active:scale-95" 
										type="submit"
									>
										<span class="material-symbols-outlined text-[18px]">badge</span>
										<span>{lang === 'ml' ? 'കാർഡ് ഡൗൺലോഡ്' : 'Download Card'}</span>
									</button>
								</form>

							<!-- OPTION 2: Enter Mobile Num for OTP Verification (Locked Feature) -->
							{:else}
								<div class="space-y-3 w-full">
									<!-- Locked notification notice -->
									<div class="p-3.5 rounded-xl bg-amber-950/70 border border-amber-500/40 text-amber-200 text-xs flex items-start gap-2.5">
										<span class="material-symbols-outlined text-amber-400 text-[18px] shrink-0 mt-0.5">lock</span>
										<div class="space-y-1 text-left">
											<p class="font-bold text-amber-300">
												{lang === 'ml' ? 'മൊബൈൽ OTP വെരിഫിക്കേഷൻ താൽക്കാലികമായി ലോക്ക് ചെയ്തിരിക്കുന്നു' : 'Mobile OTP Verification is Currently Locked'}
											</p>
											<p class="text-amber-200/90 leading-relaxed text-[11px] sm:text-xs">
												{lang === 'ml'
													? 'ടെലികോം ഡിഎൽടി (DLT) ഒടിപി ഗേറ്റ്‌വേ സുരക്ഷാ നവീകരണത്തിലാണ്. നിങ്ങളുടെ കാർഡ് ഉടനടി കാണാനും ഡൗൺലോഡ് ചെയ്യാനും മുകളിലുള്ള "Option 1: അംഗത്വ നമ്പർ" ഉപയോഗിക്കുക.'
													: 'Direct SMS OTP verification is undergoing telecom gateway compliance provisioning. To download your card immediately, please switch to Option 1 (Enter Membership ID).'}
											</p>
										</div>
									</div>

									<!-- Disabled / Preview Mobile Input -->
									<form class="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5 sm:gap-3 w-full opacity-60" onsubmit={(e) => { e.preventDefault(); handleSendOtp(); }}>
										<div class="relative flex-1 flex items-center bg-slate-100 rounded-xl border border-slate-700 overflow-hidden w-full cursor-not-allowed">
											<span class="bg-slate-200 px-3 py-2.5 sm:px-3.5 sm:py-3 text-sm text-slate-500 border-r border-slate-300 font-mono font-bold flex-shrink-0 select-none">
												+91
											</span>
											<input 
												bind:value={trackPhone}
												disabled
												class="w-full min-w-0 px-3 py-2.5 sm:px-3.5 sm:py-3 text-sm text-slate-500 placeholder:text-slate-400 bg-transparent focus:outline-none cursor-not-allowed font-medium" 
												placeholder={lang === 'ml' ? 'ഫോൺ നമ്പർ / 10-digit Mobile (Locked)' : '10-digit Mobile Number (Locked)'} 
												type="tel"
											/>
										</div>
										<button 
											class="px-5 py-3 sm:py-3.5 rounded-xl bg-slate-800 text-slate-400 border border-slate-700 text-xs sm:text-sm font-semibold flex items-center justify-center gap-2 cursor-not-allowed flex-shrink-0" 
											type="submit"
										>
											<span class="material-symbols-outlined text-[16px]">lock</span>
											<span>{lang === 'ml' ? 'Send OTP (ലോക്ക്ഡ്)' : 'Send OTP (Locked)'}</span>
										</button>
									</form>

									<button 
										type="button" 
										onclick={() => { accessMode = 'id'; statusMessage = ''; }} 
										class="text-xs text-amber-400 hover:text-amber-300 underline font-semibold flex items-center gap-1 pt-0.5"
									>
										<span class="material-symbols-outlined text-[14px]">arrow_back</span>
										<span>{lang === 'ml' ? 'അംഗത്വ നമ്പർ ഉപയോഗിക്കാൻ Option 1 ലേക്ക് മാറുക' : 'Switch back to Option 1: Enter Membership ID'}</span>
									</button>
								</div>
							{/if}

							{#if statusMessage}
								<div class={`mt-2 text-xs flex items-center gap-2 p-2.5 rounded-lg ${statusType === 'error' ? 'bg-red-950/80 text-red-200 border border-red-800' : statusType === 'success' ? 'bg-emerald-950/80 text-emerald-200 border border-emerald-800' : 'bg-amber-950/80 text-amber-200 border border-amber-800'}`}>
									<span class="material-symbols-outlined text-[16px] flex-shrink-0">{statusType === 'error' ? 'error' : statusType === 'success' ? 'check_circle' : 'info'}</span>
									<span class="font-medium break-words">{statusMessage}</span>
								</div>
							{/if}
						</div>
					</div>
				</div>
			</div>
		</section>
	</div>
</main>

<!-- Modern Clean Footer -->
<footer class="w-full bg-slate-900 text-slate-400 border-t border-slate-800 py-10">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center flex flex-col items-center justify-center gap-3">
		<div class="flex items-center gap-2.5 text-white font-bold text-sm">
			<img src="/gigLogo.png" alt="CITU Gig Workers Official Logo" class="w-6 h-6 object-contain" />
			<span>GigWorkers<span class="text-primary">.Online</span> · Kerala Gig &amp; Platform Workers Union (affil. CITU)</span>
		</div>
		<p class={`text-xs text-slate-300 font-medium max-w-2xl ${lang === 'ml' ? 'leading-[1.9]' : 'leading-normal'}`}>
			{lang === 'ml' 
				? 'രജിസ്ട്രേഷൻ നമ്പർ: Tu19965 · ഇ. ബാലാനന്ദ സ്മാരക ഓഫീസ്, സിഐടിയു സംസ്ഥാന കമ്മിറ്റി ഓഫീസ്, മേലെ തമ്പാനൂർ, തമ്പാനൂർ പി.ഒ.' 
				: 'Reg. No: Tu19965 · E Balananda Smaraka Office, CITU State Committee Office, Mele Thampanoor, Thampanoor P.O.'}
		</p>
		<div class="flex flex-wrap items-center justify-center gap-x-4 gap-y-1 text-xs text-slate-400">
			<span class="flex items-center gap-1.5">
				<span class="material-symbols-outlined text-[15px] text-amber-400">call</span>
				<span>{lang === 'ml' ? 'ഫോൺ' : 'Ph'}: <a href="tel:9846063666" class="text-slate-200 hover:text-white hover:underline font-semibold">9846063666</a>, <a href="tel:9447695655" class="text-slate-200 hover:text-white hover:underline font-semibold">9447695655</a></span>
			</span>
			<span class="text-slate-600 hidden sm:inline">•</span>
			<span>Statutory Labour Protection &amp; Civic Dignity · Copyright © 2026</span>
		</div>
		<div class="flex flex-wrap items-center justify-center gap-4 text-xs text-slate-500 mt-2">
			<span>തിരുവനന്തപുരം (TVM)</span>
			<span>•</span>
			<span>കൊച്ചി (EKM)</span>
			<span>•</span>
			<span>കോഴിക്കോട് (KKD)</span>
			<span>•</span>
			<span>തൃശ്ശൂർ (TSR)</span>
		</div>
	</div>
</footer>
