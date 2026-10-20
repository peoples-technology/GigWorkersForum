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
	<title>{lang === 'ml' ? 'KSGPWU · സിഐടിയു കേരള ഗിഗ് വർക്കേഴ്സ് യൂണിയൻ' : 'KSGPWU · CITU Kerala Gig Workers Union'}</title>
</svelte:head>

<!-- Sticky Header -->
<header class="fixed top-0 w-full z-50 bg-surface-container-lowest border-b border-surface-variant shadow-[0_1px_3px_rgba(17,24,39,0.05),0_1px_2px_rgba(17,24,39,0.03)]">
	<div class="h-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between gap-4">
		<!-- Union Logo & Title -->
		<a href="/" class="flex items-center gap-3 min-w-max group">
			<div class="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-on-primary font-bold text-xl shadow-inner group-hover:scale-105 transition-transform">
				★
			</div>
			<div class="flex flex-col">
				<span class="font-bold text-base sm:text-lg text-primary tracking-tight">KSGPWU · CITU</span>
				<span class="text-[11px] sm:text-xs text-secondary uppercase tracking-wider font-medium">
					{lang === 'ml' ? 'കേരള സ്റ്റേറ്റ് ഗിഗ് & പ്ലാറ്റ്‌ഫോം വർക്കേഴ്സ് യൂണിയൻ' : 'Kerala State Gig & Platform Workers Union'}
				</span>
			</div>
		</a>

		<!-- Desktop Navigation -->
		<nav class="hidden lg:flex items-center gap-1 font-medium text-sm">
			<a href="#quick-access-banner" class="px-3.5 py-2 rounded-lg text-on-surface-variant hover:text-on-surface hover:bg-surface-container transition-all">
				{lang === 'ml' ? 'അംഗത്വം' : 'Membership'}
			</a>
			<a href="/register" class="px-3.5 py-2 rounded-lg bg-primary-container text-on-primary-container font-semibold transition-all hover:opacity-90">
				{lang === 'ml' ? 'രജിസ്ട്രേഷൻ' : 'Register'}
			</a>
			<a href="/verify" class="px-3.5 py-2 rounded-lg text-on-surface-variant hover:text-on-surface hover:bg-surface-container transition-all">
				{lang === 'ml' ? 'ഐഡി പരിശോധന' : 'Verify ID'}
			</a>
			<a href="/admin" class="px-3.5 py-2 rounded-lg text-on-surface-variant hover:text-on-surface hover:bg-surface-container transition-all flex items-center gap-1">
				<span class="material-symbols-outlined text-[18px]">admin_panel_settings</span>
				<span>{lang === 'ml' ? 'അഡ്മിൻ ലോഗിൻ' : 'Admin Login'}</span>
			</a>
		</nav>

		<!-- Right Action Strip: Language Toggle + CTA -->
		<div class="flex items-center gap-3 min-w-max">
			<!-- Language Toggle Pill -->
			<div class="inline-flex items-center bg-surface-container-low border border-surface-variant rounded-full p-1 shadow-sm">
				<button 
					type="button" 
					onclick={() => toggleLang('ml')}
					class={`px-2.5 py-1 rounded-full text-xs font-semibold transition-colors ${lang === 'ml' ? 'bg-primary text-on-primary shadow-xs' : 'text-secondary hover:text-on-surface'}`}
				>
					മലയാളം
				</button>
				<span class="text-secondary/40 text-xs px-0.5">/</span>
				<button 
					type="button" 
					onclick={() => toggleLang('en')}
					class={`px-2.5 py-1 rounded-full text-xs font-semibold transition-colors ${lang === 'en' ? 'bg-primary text-on-primary shadow-xs' : 'text-secondary hover:text-on-surface'}`}
				>
					EN
				</button>
			</div>

			<!-- Quick Register / User Action -->
			<a 
				href="/register" 
				class="hidden sm:inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-primary text-on-primary text-xs font-semibold shadow hover:bg-primary-container transition-colors"
			>
				<span class="material-symbols-outlined text-[16px]">how_to_reg</span>
				<span>{lang === 'ml' ? 'അംഗമാകുക' : 'Join'}</span>
			</a>

			<!-- Mobile Hamburger Toggle -->
			<button 
				type="button" 
				onclick={() => mobileMenuOpen = !mobileMenuOpen}
				class="lg:hidden p-2 rounded-lg text-secondary hover:text-on-surface hover:bg-surface-container"
				aria-label="Toggle menu"
			>
				<span class="material-symbols-outlined text-2xl">{mobileMenuOpen ? 'close' : 'menu'}</span>
			</button>
		</div>
	</div>

	<!-- Mobile Menu Drawer -->
	{#if mobileMenuOpen}
		<div class="lg:hidden bg-surface-container-lowest border-b border-surface-variant px-4 py-3 space-y-2">
			<a 
				href="#quick-access-banner" 
				onclick={() => mobileMenuOpen = false} 
				class="block px-3 py-2 rounded-lg text-sm font-medium text-on-surface hover:bg-surface-container"
			>
				{lang === 'ml' ? 'അംഗത്വം · Membership' : 'Membership Track'}
			</a>
			<a 
				href="/register" 
				onclick={() => mobileMenuOpen = false} 
				class="block px-3 py-2 rounded-lg text-sm font-semibold text-primary bg-primary-fixed/40"
			>
				{lang === 'ml' ? 'പുതിയ രജിസ്ട്രേഷൻ · Register (₹160)' : 'Register Member (₹160)'}
			</a>
			<a 
				href="/verify" 
				onclick={() => mobileMenuOpen = false} 
				class="block px-3 py-2 rounded-lg text-sm font-medium text-on-surface hover:bg-surface-container"
			>
				{lang === 'ml' ? 'ഐഡി പരിശോധന · Verify Member' : 'Public Verification'}
			</a>
			<a 
				href="/admin" 
				onclick={() => mobileMenuOpen = false} 
				class="block px-3 py-2 rounded-lg text-sm font-medium text-secondary hover:bg-surface-container"
			>
				{lang === 'ml' ? 'അഡ്മിൻ ലോഗിൻ · Admin Portal' : 'Admin Portal'}
			</a>
		</div>
	{/if}
</header>

<main class="w-full pt-20 bg-surface min-h-[calc(100vh-80px)]">
	<div class="flex flex-col w-full">
		<!-- Top Statutory Notification Ticker -->
		<aside aria-label="Statutory Notice" class="w-full bg-surface-container border-b border-surface-variant/80">
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2.5 flex flex-wrap items-center justify-between gap-2 text-xs text-secondary">
				<div class="flex items-center gap-2 min-w-0">
					<span class="inline-flex items-center px-2 py-0.5 rounded-full bg-primary/10 text-primary font-semibold text-[11px] uppercase tracking-wider">
						CITU Affiliated
					</span>
					<span class="truncate font-medium">
						{lang === 'ml' 
							? 'കേരള ഗിഗ് & പ്ലാറ്റ്‌ഫോം തൊഴിലാളി യൂണിയൻ · രജിസ്ട്രേഷൻ നമ്പർ: KL-07-TU-2026' 
							: 'Kerala State Gig & Platform Workers Union · Reg No: KL-07-TU-2026'}
					</span>
				</div>
				<div class="hidden sm:flex items-center gap-3 text-on-surface-variant font-medium text-xs">
					<span class="flex items-center gap-1">
						<span class="material-symbols-outlined text-[16px] text-primary">verified_user</span>
						<span>Statutory Legal Cell</span>
					</span>
					<span>•</span>
					<span class="flex items-center gap-1">
						<span class="material-symbols-outlined text-[16px] text-tertiary">support_agent</span>
						<span>{lang === 'ml' ? '14 ജില്ലാ സമിതികൾ' : '14 District Committees'}</span>
					</span>
				</div>
			</div>
		</aside>

		<!-- Hero Section: 2-Column Grid -->
		<section class="w-full py-10 lg:py-16 bg-surface">
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
				<div class="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center">
					<!-- Left Column: Copy & Actions -->
					<div class="lg:col-span-7 flex flex-col items-start pr-0 lg:pr-4">
						<div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary-fixed text-on-primary-fixed mb-5 border border-primary/20">
							<span class="w-2 h-2 rounded-full bg-primary animate-pulse"></span>
							<span class="text-xs font-semibold tracking-wide">
								{lang === 'ml' ? 'ശക്തമായ നാളെക്കായി ഒന്നിച്ച് · Unity in Solidarity' : 'Solidarity & Dignity for Kerala Platform Workers'}
							</span>
						</div>

						<h1 class="text-3xl sm:text-4xl lg:text-5xl font-bold text-on-surface tracking-tight mb-4 leading-tight">
							{lang === 'ml' 
								? 'കേരളത്തിലെ ഗിഗ് & പ്ലാറ്റ്‌ഫോം തൊഴിലാളികൾ ഒന്നിക്കുന്നു' 
								: 'Organising Kerala’s Gig & Platform Workers'}
						</h1>

						<p class="text-base sm:text-lg text-secondary max-w-2xl leading-relaxed mb-8">
							{lang === 'ml'
								? 'ഡെലിവറി പാർട്ണർമാർ, ആപ്പ് ഡ്രൈവർമാർ, പ്ലാറ്റ്‌ഫോം ജീവനക്കാർ എന്നിവർക്കായി നിയമപരിരക്ഷ, മിനിമം നിരക്ക് സ്ഥിരത, മാന്യമായ തൊഴിൽ അന്തസ്സ് എന്നിവ ഉറപ്പാക്കാൻ സിഐടിയു നേതൃത്വത്തിലുള്ള ഡിജിറ്റൽ മുന്നേറ്റം.'
								: 'A digital solidarity initiative by the Kerala State Gig & Platform Workers Union (CITU) to secure legal protection, algorithmic transparency, minimum rate parity, and civic dignity for delivery partners, app drivers, and platform personnel across all 14 districts.'}
						</p>

						<!-- Action Button Cluster -->
						<div class="flex flex-wrap items-stretch sm:items-center gap-3 w-full sm:w-auto">
							<a 
								href="/register" 
								class="inline-flex items-center justify-center gap-2.5 px-6 sm:px-7 py-3.5 rounded-lg bg-primary text-on-primary text-sm font-semibold shadow-sm hover:bg-on-primary-fixed-variant transition-all focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
							>
								<span>{lang === 'ml' ? 'അംഗമാകുക / Join the Union (₹160)' : 'Join the Union (₹160)'}</span>
								<span class="material-symbols-outlined text-[20px]">arrow_forward</span>
							</a>

							<a 
								href="#quick-access-banner"
								class="inline-flex items-center justify-center gap-2 px-5 sm:px-6 py-3.5 rounded-lg bg-surface-container-lowest border border-surface-variant text-on-surface text-sm font-semibold hover:bg-surface-container transition-all"
							>
								<span class="material-symbols-outlined text-[20px] text-secondary">search</span>
								<span>{lang === 'ml' ? 'തിരച്ചിൽ / Track Membership' : 'Track Membership'}</span>
							</a>
						</div>

						<!-- Launch Pill Badge -->
						<div class="mt-7 inline-flex items-center gap-2.5 bg-primary-fixed/50 border border-primary/30 text-primary text-xs font-medium px-4 py-2 rounded-full">
							<span class="material-symbols-outlined text-[18px]">calendar_month</span>
							<span><strong>1 November 2026</strong> · Kerala Piravi State Declaration</span>
						</div>

						<!-- Micro Metric Proofpoints -->
						<div class="mt-8 pt-6 border-t border-surface-variant w-full grid grid-cols-3 gap-4">
							<div>
								<p class="text-2xl sm:text-3xl font-bold text-on-surface">14</p>
								<p class="text-xs sm:text-sm text-secondary font-medium">
									{lang === 'ml' ? 'ജില്ലാ ഹെൽപ്പ്‌ഡെസ്ക്' : 'District Desks'}
								</p>
							</div>
							<div>
								<p class="text-2xl sm:text-3xl font-bold text-primary">₹160</p>
								<p class="text-xs sm:text-sm text-secondary font-medium">
									{lang === 'ml' ? 'വാർഷിക വിഹിതം' : 'Annual Dues'}
								</p>
							</div>
							<div>
								<p class="text-2xl sm:text-3xl font-bold text-tertiary">100%</p>
								<p class="text-xs sm:text-sm text-secondary font-medium">
									{lang === 'ml' ? 'നിയമ സുരക്ഷാ പരിരക്ഷ' : 'Legal Protection'}
								</p>
							</div>
						</div>
					</div>

					<!-- Right Column: Editorial Visual Card -->
					<div class="lg:col-span-5 relative w-full">
						<div class="relative bg-surface-container-lowest rounded-2xl p-3 border border-surface-variant shadow-[0_1px_3px_rgba(17,24,39,0.05),0_1px_2px_rgba(17,24,39,0.03)] overflow-hidden">
							<div class="w-full aspect-[4/3] rounded-xl overflow-hidden bg-surface-container-low relative">
								<img 
									class="w-full h-full object-contain" 
									alt="Solidarity artwork showing Kerala gig workers across food delivery, taxi, and courier logistics"
									src="/images/HomePage-HeroAsset.png"
									onerror={(e) => {
										// Fallback if local asset is loading
										(e.currentTarget as HTMLImageElement).src = "https://lh3.googleusercontent.com/aida-public/AB6AXuAWe4zboGWqHL3jwywJUeVISdlnK_rC41LVB4QtSYp9gdGbXwg3nD6fRYs5iOt8M-yBKUJvXlMGr2iil4ngfjS-RjAvAcZ2dfz1HkXoPrzPkgJvZpJvo1ALHS7H5co15GqKBUWOPR3EYM9MlvLYJy5bPjXcHY3Ju2yNNHqhtJpDN0ai7h5rEgRGssd7vmm5HU_EbhSFCHVgEGVItQFkp_krs51AhFOzKbDwiYmeFYXV1bUaKEZzDSVfVA";
									}}
								/>
								<!-- Subtle Floating Verified Seal Badge -->
								<div class="absolute bottom-3 left-3 bg-surface-container-lowest/95 backdrop-blur-sm px-3 py-1.5 rounded-lg border border-surface-variant flex items-center gap-2 shadow-sm">
									<span class="material-symbols-outlined text-primary text-[18px]">verified</span>
									<span class="text-xs text-on-surface font-semibold">CITU Accredited State Portal</span>
								</div>
							</div>
							<!-- Mini Caption Strip -->
							<div class="px-2 pt-3 pb-1 flex items-center justify-between text-secondary text-xs">
								<span>{lang === 'ml' ? 'ഡെലിവറി • ക്യാബ് • ലോജിസ്റ്റിക്സ്' : 'Delivery • Cab • Logistics'}</span>
								<span class="text-primary font-semibold">Kerala State Chapter</span>
							</div>
						</div>
					</div>
				</div>
			</div>
		</section>

		<!-- Three Feature Highlights -->
		<section class="w-full py-12 bg-surface-container-low border-y border-surface-variant">
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
				<div class="flex flex-col md:flex-row md:items-end justify-between mb-8 gap-2">
					<div>
						<span class="text-primary text-xs uppercase tracking-wider font-bold">
							{lang === 'ml' ? 'ഡിജിറ്റൽ ആനുകൂല്യങ്ങൾ' : 'Digital Protections'}
						</span>
						<h2 class="text-xl sm:text-2xl font-bold text-on-surface tracking-tight mt-1">
							{lang === 'ml' ? 'തൊഴിലാളി ക്ഷേമവും അംഗത്വ ആനുകൂല്യങ്ങളും' : 'Platform Protections & Member Services'}
						</h2>
					</div>
					<p class="text-xs sm:text-sm text-secondary max-w-md">
						{lang === 'ml' 
							? 'കേരളത്തിലെ എല്ലാ ഡെലിവറി, ക്യാബ്, ഇ-കൊമേഴ്സ് ഗിഗ് തൊഴിലാളികൾക്കും വിരൽത്തുമ്പിൽ സഹായം.' 
							: 'Designed for frictionless operation in Kerala’s delivery, transport, and digital work sectors.'}
					</p>
				</div>

				<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
					<!-- Feature 1 -->
					<article class="bg-surface-container-lowest p-6 rounded-xl border border-surface-variant shadow-[0_1px_3px_rgba(17,24,39,0.05),0_1px_2px_rgba(17,24,39,0.03)] flex flex-col justify-between hover:border-primary/40 transition-colors">
						<div>
							<div class="w-12 h-12 rounded-lg bg-primary-fixed flex items-center justify-center text-primary mb-5">
								<span class="material-symbols-outlined text-[26px]">phonelink_lock</span>
							</div>
							<h3 class="text-lg font-bold text-on-surface mb-2">
								{lang === 'ml' ? 'സ്വയം രജിസ്ട്രേഷൻ' : 'Instant Registration'}
							</h3>
							<p class="text-sm text-secondary leading-relaxed">
								{lang === 'ml'
									? 'മൊബൈൽ ഒടിപി വഴി മിനിറ്റുകൾക്കുള്ളിൽ വേരിഫിക്കേഷൻ. സ്വിഗ്ഗി, സൊമാറ്റോ, ഊബർ, ഒല, ആമസോൺ തൊഴിലാളികൾക്ക് ലളിതമായ രജിസ്ട്രേഷൻ.'
									: 'Verified instantly via secure mobile SMS OTP. Enter your vehicle or delivery partner ID for automated activation across Zomato, Swiggy, Uber, Ola, and courier platforms.'}
							</p>
						</div>
						<div class="mt-6 pt-4 border-t border-surface-variant flex items-center gap-2 text-primary text-xs font-semibold">
							<span>{lang === 'ml' ? '2 മിനിറ്റിനകം ആക്റ്റീവ്' : 'Active in 2 minutes'}</span>
							<span class="material-symbols-outlined text-[16px]">check_circle</span>
						</div>
					</article>

					<!-- Feature 2 -->
					<article class="bg-surface-container-lowest p-6 rounded-xl border border-surface-variant shadow-[0_1px_3px_rgba(17,24,39,0.05),0_1px_2px_rgba(17,24,39,0.03)] flex flex-col justify-between hover:border-primary/40 transition-colors">
						<div>
							<div class="w-12 h-12 rounded-lg bg-tertiary-fixed flex items-center justify-center text-tertiary mb-5">
								<span class="material-symbols-outlined text-[26px]">badge</span>
							</div>
							<h3 class="text-lg font-bold text-on-surface mb-2">
								{lang === 'ml' ? 'ഡിജിറ്റൽ അംഗത്വ കാർഡ്' : 'Digital Membership ID Card'}
							</h3>
							<p class="text-sm text-secondary leading-relaxed">
								{lang === 'ml'
									? 'തത്സമയം ഡൗൺലോഡ് ചെയ്യാവുന്ന ക്രിപ്റ്റോഗ്രാഫിക് ക്യുആർ കോഡ് അടങ്ങിയ യൂണിയൻ ഡിജിറ്റൽ തിരിച്ചറിയൽ കാർഡ്.'
									: 'Instantly generate an authenticated digital union membership ID card carrying a dynamic cryptographically verified QR seal for roadside verification and labour claims.'}
							</p>
						</div>
						<div class="mt-6 pt-4 border-t border-surface-variant flex items-center gap-2 text-tertiary text-xs font-semibold">
							<span>{lang === 'ml' ? 'QR-സ്ഥിരീകരിച്ച ഐഡി' : 'Cryptographic QR Seal'}</span>
							<span class="material-symbols-outlined text-[16px]">qr_code_scanner</span>
						</div>
					</article>

					<!-- Feature 3 -->
					<article class="bg-surface-container-lowest p-6 rounded-xl border border-surface-variant shadow-[0_1px_3px_rgba(17,24,39,0.05),0_1px_2px_rgba(17,24,39,0.03)] flex flex-col justify-between hover:border-primary/40 transition-colors">
						<div>
							<div class="w-12 h-12 rounded-lg bg-secondary-fixed flex items-center justify-center text-on-secondary-fixed-variant mb-5">
								<span class="material-symbols-outlined text-[26px]">support</span>
							</div>
							<h3 class="text-lg font-bold text-on-surface mb-2">
								{lang === 'ml' ? 'സഹായം & പരാതി പരിഹാരം' : 'Helpline & Grievance'}
							</h3>
							<p class="text-sm text-secondary leading-relaxed">
								{lang === 'ml'
									? '14 ജില്ലകളിലും അന്യായമായ ഐഡി ബ്ലോക്കിംഗിനെതിരെ നിയമസഹായം, അപകട ഇൻഷുറൻസ് ക്ലെയിം സഹായം, ഒത്തുതീർപ്പ് സമിതികൾ.'
									: 'Direct access to all 14-district worker conciliation committees, legal aid desks for wrongful platform deactivation, and immediate accident assistance squads.'}
							</p>
						</div>
						<div class="mt-6 pt-4 border-t border-surface-variant flex items-center gap-2 text-on-secondary-fixed-variant text-xs font-semibold">
							<span>{lang === 'ml' ? '24/7 നിയമ സഹായം' : '24/7 Legal Assistance'}</span>
							<span class="material-symbols-outlined text-[16px]">call</span>
						</div>
					</article>
				</div>
			</div>
		</section>

		<!-- Member Quick Access Banner -->
		<section class="w-full py-12 bg-surface" id="quick-access-banner">
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
				<div class="bg-on-background text-on-primary rounded-2xl p-6 sm:p-8 lg:p-10 border border-surface-variant/30 shadow-md">
					<div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
						<!-- Text Lockup -->
						<div class="lg:col-span-6">
							<div class="inline-flex items-center gap-2 px-2.5 py-1 rounded bg-surface-container-highest/20 text-on-tertiary-container text-xs font-medium mb-3">
								<span class="material-symbols-outlined text-[16px] text-primary-fixed-dim">lock</span>
								<span>{lang === 'ml' ? 'നിലവിലുള്ള അംഗങ്ങൾക്കായി · Portal Access' : 'Existing Members · Quick Access'}</span>
							</div>
							<h3 class="text-xl sm:text-2xl font-bold text-on-primary">
								{lang === 'ml' ? 'നിങ്ങളുടെ അംഗത്വം പരിശോധിക്കുക' : 'Access Your Membership'}
							</h3>
							<p class="text-xs sm:text-sm text-surface-variant mt-2 max-w-lg leading-relaxed">
								{lang === 'ml'
									? 'രജിസ്റ്റർ ചെയ്ത 10 അക്ക മൊബൈൽ നമ്പർ നൽകി അപേക്ഷയുടെ നില പരിശോധിക്കുക, ഡിജിറ്റൽ തിരിച്ചറിയൽ കാർഡ് ഡൗൺലോഡ് ചെയ്യുക, അല്ലെങ്കിൽ വാർഷിക വിഹിതം അടയ്ക്കുക.'
									: 'Enter your registered 10-digit mobile number to track application status, download your high-resolution digital ID card, or pay annual union subscriptions.'}
							</p>
						</div>

						<!-- Input Action Form -->
						<div class="lg:col-span-6 w-full">
							<form class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3" onsubmit={(e) => { e.preventDefault(); handleSendOtp(); }}>
								<div class="relative flex-1 flex items-center bg-surface-container-lowest rounded-lg border border-surface-variant overflow-hidden focus-within:ring-2 focus-within:ring-primary focus-within:border-primary">
									<span class="bg-surface-container px-3.5 py-3 text-sm text-secondary border-r border-surface-variant flex items-center select-none font-mono font-medium">
										+91
									</span>
									<input 
										bind:value={trackPhone}
										class="w-full px-3 py-3 text-sm text-on-surface placeholder:text-secondary/60 bg-transparent focus:outline-none" 
										id="track-input" 
										maxlength="10" 
										pattern="[0-9]{10}" 
										placeholder={lang === 'ml' ? 'ഫോൺ നമ്പർ / 10-digit Mobile' : '10-digit Mobile Number'} 
										required 
										type="tel"
									/>
								</div>
								<button 
									class="px-6 py-3.5 rounded-lg bg-primary hover:bg-on-primary-fixed-variant text-on-primary text-sm font-semibold whitespace-nowrap transition-colors flex items-center justify-center gap-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-70" 
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
								<div class={`mt-3 text-xs flex items-center gap-2 ${statusType === 'error' ? 'text-error-container' : 'text-primary-fixed'}`}>
									<span class="material-symbols-outlined text-[16px]">{statusType === 'error' ? 'error' : 'info'}</span>
									<span>{statusMessage}</span>
								</div>
							{/if}
						</div>
					</div>
				</div>
			</div>
		</section>
	</div>
</main>

<!-- Footer -->
<footer class="w-full bg-surface-container-lowest border-t border-surface-variant py-8">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center flex flex-col items-center justify-center gap-2">
		<p class="text-xs sm:text-sm text-secondary">
			Kerala State Gig &amp; Platform Workers Union (affil. CITU) · Registration: KL-07-TU-2026 · Copyright © 2026
		</p>
		<div class="flex flex-wrap items-center justify-center gap-3 text-secondary text-xs mt-1">
			<span>തിരുവനന്തപുരം · കൊച്ചി · കോഴിക്കോട്</span>
			<span>•</span>
			<span>Statutory Labour Protection &amp; Civic Dignity</span>
			<span>•</span>
			<a href="/admin" class="text-primary hover:underline font-semibold">Admin Console</a>
		</div>
	</div>
</footer>
