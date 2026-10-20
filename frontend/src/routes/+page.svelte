<script lang="ts">
	let lang = $state<'ml' | 'en'>('ml');
	let mobileMenuOpen = $state(false);

	// Tracking / OTP Form state
	let trackPhone = $state('');
	let otpSending = $state(false);
	let otpSent = $state(false);
	let statusMessage = $state('');
	let statusType = $state<'info' | 'error' | 'success'>('info');

	function toggleLang(newLang: 'ml' | 'en') {
		lang = newLang;
	}

	function handleSendOtp() {
		if (!trackPhone || trackPhone.length < 10) {
			statusType = 'error';
			statusMessage = lang === 'ml' 
				? 'ദയവായി സാധുവായ 10 അക്ക മൊബൈൽ നമ്പർ നൽകുക.' 
				: 'Please enter a valid 10-digit mobile number.';
			return;
		}

		otpSending = true;
		statusMessage = '';

		setTimeout(() => {
			otpSending = false;
			otpSent = true;
			statusType = 'success';
			statusMessage = lang === 'ml'
				? `OTP +91 ${trackPhone} എന്ന നമ്പറിലേക്ക് അയച്ചിട്ടുണ്ട്. Verification window activated.`
				: `OTP has been dispatched to +91 ${trackPhone}. Verification window activated.`;
		}, 900);
	}
</script>

<svelte:head>
	<title>{lang === 'ml' ? 'GigWorkers.Online · കേരള ഗിഗ് & പ്ലാറ്റ്‌ഫോം വർക്കേഴ്സ് യൂണിയൻ' : 'GigWorkers.Online · Kerala Gig & Platform Workers Union'}</title>
</svelte:head>

<!-- Frosted Glass Sticky Header -->
<header class="fixed top-0 w-full z-50 bg-white/90 backdrop-blur-md border-b border-slate-200/80 shadow-sm transition-all">
	<div class="h-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between gap-4">
		<!-- Union Logo & Title -->
		<a href="/" class="flex items-center gap-3.5 min-w-max group">
			<div class="w-11 h-11 rounded-xl bg-gradient-to-br from-red-600 via-primary to-red-900 flex items-center justify-center text-white font-black text-2xl shadow-md shadow-red-700/20 group-hover:scale-105 group-hover:rotate-1 transition-transform">
				★
			</div>
			<div class="flex flex-col">
				<div class="flex items-center gap-2">
					<span class="font-extrabold text-base sm:text-lg text-slate-900 tracking-tight group-hover:text-primary transition-colors">
						GigWorkers<span class="text-primary">.Online</span>
					</span>
					<span class="hidden sm:inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-100 text-red-800 border border-red-200 uppercase tracking-wide">
						Kerala
					</span>
				</div>
				<span class="text-[11px] sm:text-xs text-slate-500 uppercase tracking-wider font-medium">
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

		<!-- Right Action Strip: Language Toggle + Register CTA -->
		<div class="flex items-center gap-3 min-w-max">
			<!-- Language Toggle Pill -->
			<div class="inline-flex items-center bg-slate-100/90 border border-slate-200 rounded-full p-1 shadow-inner">
				<button 
					type="button" 
					onclick={() => toggleLang('ml')}
					class={`px-3 py-1 rounded-full text-xs font-bold transition-all ${lang === 'ml' ? 'bg-primary text-white shadow-sm' : 'text-slate-600 hover:text-slate-900'}`}
				>
					മലയാളം
				</button>
				<button 
					type="button" 
					onclick={() => toggleLang('en')}
					class={`px-3 py-1 rounded-full text-xs font-bold transition-all ${lang === 'en' ? 'bg-primary text-white shadow-sm' : 'text-slate-600 hover:text-slate-900'}`}
				>
					EN
				</button>
			</div>

			<!-- Quick Register CTA Button -->
			<a 
				href="/register" 
				class="hidden sm:inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl crimson-gradient-btn text-white text-xs font-bold tracking-wide shadow-md"
			>
				<span class="material-symbols-outlined text-[16px]">how_to_reg</span>
				<span>{lang === 'ml' ? 'അംഗമാകുക (₹100)' : 'Join Union (₹100)'}</span>
			</a>

			<!-- Mobile Hamburger Toggle -->
			<button 
				type="button" 
				onclick={() => mobileMenuOpen = !mobileMenuOpen}
				class="lg:hidden p-2 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100"
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
				{lang === 'ml' ? 'അംഗത്വം · Membership' : 'Membership Track'}
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

<main class="w-full pt-20 min-h-[calc(100vh-80px)]">
	<div class="flex flex-col w-full">
		<!-- Top Statutory Notification Ticker -->
		<aside aria-label="Statutory Notice" class="w-full bg-gradient-to-r from-red-950 via-slate-900 to-red-950 text-white border-b border-red-900/40">
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2.5 flex flex-wrap items-center justify-between gap-2 text-xs">
				<div class="flex items-center gap-2.5 min-w-0">
					<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-red-600 text-white font-bold text-[10px] uppercase tracking-wider shadow-xs">
						★ CITU Affiliated
					</span>
					<span class="truncate font-medium text-slate-200">
						{lang === 'ml' 
							? 'കേരള ഗിഗ് & പ്ലാറ്റ്‌ഫോം തൊഴിലാളി യൂണിയൻ · രജിസ്ട്രേഷൻ നമ്പർ: KL-07-TU-2026' 
							: 'GigWorkers.Online · Kerala Gig Workers Union · Reg No: KL-07-TU-2026'}
					</span>
				</div>
				<div class="hidden sm:flex items-center gap-4 text-slate-300 font-medium text-xs">
					<span class="flex items-center gap-1.5">
						<span class="material-symbols-outlined text-[16px] text-amber-400">verified_user</span>
						<span>Statutory Legal Cell</span>
					</span>
					<span class="text-slate-600">•</span>
					<span class="flex items-center gap-1.5">
						<span class="material-symbols-outlined text-[16px] text-blue-400">support_agent</span>
						<span>{lang === 'ml' ? '14 ജില്ലാ സമിതികൾ' : '14 District Committees'}</span>
					</span>
				</div>
			</div>
		</aside>

		<!-- Hero Section -->
		<section class="w-full bg-white py-12 lg:py-20 relative overflow-hidden">
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
				<div class="grid grid-cols-1 lg:grid-cols-2 gap-10 lg:gap-16 items-center">

					<!-- Left Column: Copy & Actions -->
					<div class="flex flex-col items-start">

						<!-- Union Affiliation Badge -->
						<div class="inline-flex items-center gap-2.5 px-4 py-2 rounded-sm bg-primary text-white mb-7 shadow-sm">
							<div class="flex flex-col leading-tight">
								<span class="text-[11px] font-black tracking-widest uppercase">Kerala Gig &amp; Platform Workers Union</span>
								<span class="text-[10px] font-medium opacity-90">(Affiliated to CITU)</span>
							</div>
							<!-- Hammer & Sickle -->
							<svg class="w-7 h-7 flex-shrink-0" viewBox="0 0 100 100" fill="white" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
								<!-- Hammer handle -->
								<rect x="10" y="50" width="55" height="9" rx="3" transform="rotate(-45 37 54)"/>
								<!-- Hammer head -->
								<rect x="2" y="12" width="30" height="16" rx="3" transform="rotate(-45 17 20)"/>
								<!-- Sickle arc -->
								<path d="M 55 70 A 28 28 0 1 1 83 42" stroke="white" stroke-width="9" fill="none" stroke-linecap="round"/>
								<!-- Sickle blade tip -->
								<path d="M 78 36 L 90 30 L 87 44 Z"/>
							</svg>
						</div>

						<!-- Bilingual Headline -->
						<h1 class="font-black text-slate-900 mb-4 leading-tight tracking-tight">
							{#if lang === 'ml'}
								<span class="block text-4xl sm:text-5xl lg:text-[3.5rem]" style="font-family: 'Noto Sans Malayalam', sans-serif; line-height: 1.25;">
									ശക്തമായ<br/>നാളെക്കായി ഒന്നിച്ച്
								</span>
							{:else}
								<span class="block text-4xl sm:text-5xl lg:text-[3.5rem] leading-tight">
									United for a
								</span>
								<span class="block text-4xl sm:text-5xl lg:text-[3.5rem] text-primary font-black italic leading-tight">
									stronger tomorrow
								</span>
							{/if}
						</h1>

						<!-- Subtitle -->
						<p class="text-base sm:text-lg text-slate-500 leading-relaxed mb-9">
							{lang === 'ml'
								? 'കേരളത്തിലെ ഗിഗ് & പ്ലാറ്റ്‌ഫോം തൊഴിലാളികളെ സംഘടിപ്പിക്കുന്നു'
								: "Organising Kerala's Gig & Platform Workers"}
						</p>

						<!-- CTA Buttons -->
						<div class="flex flex-wrap items-center gap-4 w-full sm:w-auto">
							<a
								href="/register"
								class="inline-flex items-center justify-center gap-2 px-7 py-3.5 rounded-md bg-primary hover:bg-[#80000f] text-white text-sm font-bold tracking-wide shadow-md transition-colors"
							>
								<span style="font-family: 'Noto Sans Malayalam', sans-serif;">അംഗമാകുക</span>
								<span class="opacity-50">|</span>
								<span class="uppercase tracking-wider text-xs font-black">Join the Union</span>
								<span class="material-symbols-outlined text-[18px]">arrow_forward</span>
							</a>

							<a
								href="#quick-access-banner"
								class="inline-flex items-center justify-center gap-2.5 px-6 py-3.5 rounded-md bg-white border border-slate-300 text-slate-800 text-sm font-semibold hover:bg-slate-50 hover:border-slate-400 transition-all shadow-sm"
							>
								<span style="font-family: 'Noto Sans Malayalam', sans-serif;">{lang === 'ml' ? 'തിരച്ചിൽ' : 'തിരച്ചിൽ'}</span>
								<span class="opacity-40">|</span>
								<span>Track Membership</span>
							</a>
						</div>

						<!-- Stats strip -->
						<div class="mt-10 pt-8 border-t border-slate-100 w-full grid grid-cols-3 gap-6">
							<div>
								<p class="text-2xl sm:text-3xl font-black text-slate-900">14</p>
								<p class="text-[11px] text-slate-400 font-semibold mt-1 uppercase tracking-widest">
									{lang === 'ml' ? 'ജില്ലകൾ' : 'Districts'}
								</p>
							</div>
							<div>
								<p class="text-2xl sm:text-3xl font-black text-primary">₹100</p>
								<p class="text-[11px] text-slate-400 font-semibold mt-1 uppercase tracking-widest">
									{lang === 'ml' ? 'രജിസ്ട്രേഷൻ ഫീസ്' : 'Registration Fee'}
								</p>
							</div>
							<div>
								<p class="text-2xl sm:text-3xl font-black text-emerald-600">100%</p>
								<p class="text-[11px] text-slate-400 font-semibold mt-1 uppercase tracking-widest">
									{lang === 'ml' ? 'നിയമ സുരക്ഷ' : 'Legal Cover'}
								</p>
							</div>
						</div>
					</div>

					<!-- Right Column: Hero Illustration -->
					<div class="relative flex items-center justify-center w-full lg:justify-end">
						<img
							src="/images/HomePage-HeroAsset.png"
							alt="Kerala gig workers — delivery partners, cab drivers, and platform workers standing united with a CITU flag"
							class="w-full max-w-lg lg:max-w-none object-contain select-none"
							onerror={(e) => {
								(e.currentTarget as HTMLImageElement).src = "https://lh3.googleusercontent.com/aida-public/AB6AXuAWe4zboGWqHL3jwywJUeVISdlnK_rC41LVB4QtSYp9gdGbXwg3nD6fRYs5iOt8M-yBKUJvXlMGr2iil4ngfjS-RjAvAcZ2dfz1HkXoPrzPkgJvZpJvo1ALHS7H5co15GqKBUWOPR3EYM9MlvLYJy5bPjXcHY3Ju2yNNHqhtJpDN0ai7h5rEgRGssd7vmm5HU_EbhSFCHVgEGVItQFkp_krs51AhFOzKbDwiYmeFYXV1bUaKEZzDSVfVA";
							}}
						/>
					</div>

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
					<p class="text-xs sm:text-sm text-slate-600 max-w-md">
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
							<p class="text-sm text-slate-600 leading-relaxed">
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
							<p class="text-sm text-slate-600 leading-relaxed">
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
							<p class="text-sm text-slate-600 leading-relaxed">
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
		<section class="w-full py-16 bg-white" id="quick-access-banner">
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
				<div class="bg-gradient-to-br from-slate-950 via-slate-900 to-red-950 text-white rounded-3xl p-8 sm:p-10 lg:p-12 border border-slate-800 shadow-2xl relative overflow-hidden">
					<!-- Ambient Glow Inside Card -->
					<div class="absolute -top-20 -right-20 w-80 h-80 bg-red-600/15 rounded-full blur-3xl pointer-events-none"></div>

					<div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center relative z-10">
						<!-- Text Lockup -->
						<div class="lg:col-span-6">
							<div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-900/40 text-red-300 border border-red-500/30 text-xs font-bold mb-4">
								<span class="material-symbols-outlined text-[16px]">lock</span>
								<span>{lang === 'ml' ? 'നിലവിലുള്ള അംഗങ്ങൾക്കായി · Portal Access' : 'Existing Members · Quick Access'}</span>
							</div>
							<h3 class="text-2xl sm:text-3xl font-black text-white">
								{lang === 'ml' ? 'നിങ്ങളുടെ അംഗത്വം പരിശോധിക്കുക' : 'Access Your Membership'}
							</h3>
							<p class="text-xs sm:text-sm text-slate-300 mt-2.5 max-w-lg leading-relaxed">
								{lang === 'ml'
									? 'രജിസ്റ്റർ ചെയ്ത 10 അക്ക മൊബൈൽ നമ്പർ നൽകി അപേക്ഷയുടെ നില പരിശോധിക്കുക, ഡിജിറ്റൽ തിരിച്ചറിയൽ കാർഡ് ഡൗൺലോഡ് ചെയ്യുക, അല്ലെങ്കിൽ വാർഷിക വിഹിതം അടയ്ക്കുക.'
									: 'Enter your registered 10-digit mobile number to track application status, download your high-resolution digital ID card, or renew your membership.'}
							</p>
						</div>

						<!-- Input Action Form -->
						<div class="lg:col-span-6 w-full">
							<form class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3" onsubmit={(e) => { e.preventDefault(); handleSendOtp(); }}>
								<div class="relative flex-1 flex items-center bg-white/95 rounded-xl border border-slate-300 overflow-hidden shadow-sm focus-within:ring-2 focus-within:ring-primary focus-within:border-primary">
									<span class="bg-slate-100 px-3.5 py-3 text-sm text-slate-700 border-r border-slate-300 flex items-center select-none font-mono font-bold">
										+91
									</span>
									<input 
										bind:value={trackPhone}
										class="w-full px-3.5 py-3 text-sm text-slate-900 placeholder:text-slate-400 bg-transparent focus:outline-none font-medium" 
										id="track-input" 
										maxlength="10" 
										pattern="[0-9]{10}" 
										placeholder={lang === 'ml' ? 'ഫോൺ നമ്പർ / 10-digit Mobile' : '10-digit Mobile Number'} 
										required 
										type="tel"
									/>
								</div>
								<button 
									class="px-7 py-3.5 rounded-xl crimson-gradient-btn text-white text-sm font-bold whitespace-nowrap flex items-center justify-center gap-2 disabled:opacity-70 shadow-lg" 
									id="otp-btn" 
									type="submit"
									disabled={otpSending}
								>
									{#if otpSending}
										<span class="material-symbols-outlined animate-spin text-[18px]">progress_activity</span>
										<span>{lang === 'ml' ? 'അയക്കുന്നു...' : 'Sending...'}</span>
									{:else if otpSent}
										<span class="material-symbols-outlined text-[18px]">done</span>
										<span>{lang === 'ml' ? 'OTP പരിശോധിക്കുക' : 'Verify OTP'}</span>
									{:else}
										<span>{lang === 'ml' ? 'OTP അയക്കുക' : 'Send OTP'}</span>
										<span class="material-symbols-outlined text-[18px]">sms</span>
									{/if}
								</button>
							</form>

							{#if statusMessage}
								<div class={`mt-3 text-xs flex items-center gap-2 p-2.5 rounded-lg ${statusType === 'error' ? 'bg-red-950/80 text-red-200 border border-red-800' : 'bg-emerald-950/80 text-emerald-200 border border-emerald-800'}`}>
									<span class="material-symbols-outlined text-[16px]">{statusType === 'error' ? 'error' : 'check_circle'}</span>
									<span class="font-medium">{statusMessage}</span>
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
		<div class="flex items-center gap-2 text-white font-bold text-sm">
			<span class="text-primary text-xl">★</span>
			<span>GigWorkers<span class="text-primary">.Online</span> · Kerala Gig &amp; Platform Workers Union (affil. CITU)</span>
		</div>
		<p class="text-xs text-slate-400">
			Registration: KL-07-TU-2026 · Statutory Labour Protection &amp; Civic Dignity · Copyright © 2026
		</p>
		<div class="flex flex-wrap items-center justify-center gap-4 text-xs text-slate-400 mt-2">
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
