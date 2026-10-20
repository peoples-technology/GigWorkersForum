<script lang="ts">
	import { onMount } from 'svelte';

	let lang = $state<'ml' | 'en'>('ml');
	let isLoggedIn = $state(true);
	let currentNav = $state<'overview' | 'members' | 'dues' | 'districts' | 'grievances' | 'import' | 'audit'>('overview');
	
	// Search and filter
	let searchQuery = $state('');
	let selectedDistrict = $state('All');
	let selectedCategory = $state<'all' | 'delivery' | 'ride' | 'services'>('all');
	
	// Modal states
	let showImportModal = $state(false);
	let selectedMemberForModal = $state<any>(null);
	let importFile: File | null = $state(null);
	let importDistrict = $state('KLERN');
	let importCollector = $state('Com. K. Balakrishnan');
	let importSuccess = $state(false);

	// Auth credentials (if logged out)
	let username = $state('state_gs');
	let password = $state('CITUSolidarity@2026');
	let totp = $state('REC001AA');
	let authStep = $state<'cred' | '2fa'>('cred');
	let authError = $state('');

	// Sample Members data matching Civic Vanguard schema
	let membersList = $state([
		{
			id: 'KLTVC000009',
			name: 'Anandhu K. S.',
			avatar: 'AK',
			role: 'Delivery Partner · Food & Grocery',
			district: 'തിരുവനന്തപുരം / TVC',
			districtCode: 'KLTVC',
			platform: 'Zomato',
			category: 'delivery',
			date: '20 Oct 2026, 14:22',
			status: 'active',
			paidUpTo: 'Oct 2027',
			phone: '+919847000009'
		},
		{
			id: 'KLERN000142',
			name: 'Fathima Zahra',
			avatar: 'FZ',
			role: 'Taxi Cab Driver · Airport Fleet',
			district: 'എറണാകുളം / ERN',
			districtCode: 'KLERN',
			platform: 'Uber',
			category: 'ride',
			date: '20 Oct 2026, 13:50',
			status: 'active',
			paidUpTo: 'Oct 2027',
			phone: '+919847000142'
		},
		{
			id: 'KLKZD000219',
			name: 'Rahul V. Nair',
			avatar: 'RN',
			role: 'Courier Pilot · Hyperlocal',
			district: 'കോഴിക്കോട് / KZD',
			districtCode: 'KLKZD',
			platform: 'Swiggy',
			category: 'delivery',
			date: '20 Oct 2026, 12:15',
			status: 'active',
			paidUpTo: 'Oct 2027',
			phone: '+919847000219'
		},
		{
			id: 'KLTCR000088',
			name: 'Muhammed Shafi',
			avatar: 'MS',
			role: 'Auto Pilot · City Express',
			district: 'തൃശ്ശൂർ / TCR',
			districtCode: 'KLTCR',
			platform: 'Rapido',
			category: 'ride',
			date: '20 Oct 2026, 11:40',
			status: 'active',
			paidUpTo: 'Oct 2027',
			phone: '+919847000088'
		},
		{
			id: 'KLKLM000305',
			name: 'Jisha B.',
			avatar: 'JB',
			role: 'Food Delivery Associate',
			district: 'കൊല്ലം / KLM',
			districtCode: 'KLKLM',
			platform: 'Zomato',
			category: 'delivery',
			date: '20 Oct 2026, 10:05',
			status: 'active',
			paidUpTo: 'Oct 2027',
			phone: '+919847000305'
		},
		{
			id: 'KLKTM000052',
			name: 'Thomas George',
			avatar: 'TG',
			role: 'Cargo Mini-Truck Operator',
			district: 'കോട്ടയം / KTM',
			districtCode: 'KLKTM',
			platform: 'Porter',
			category: 'services',
			date: '20 Oct 2026, 09:30',
			status: 'pending',
			paidUpTo: 'Pending Docs',
			phone: '+919847000052'
		}
	]);

	let filteredMembers = $derived(
		membersList.filter((m) => {
			const matchesSearch = !searchQuery || 
				m.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
				m.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
				m.phone.includes(searchQuery);
			
			const matchesDistrict = selectedDistrict === 'All' || m.districtCode === selectedDistrict;
			
			const matchesCategory = selectedCategory === 'all' || m.category === selectedCategory;

			return matchesSearch && matchesDistrict && matchesCategory;
		})
	);

	function exportCSV() {
		const headers = ['ID,Name,Phone,District,Platform,Status,Date'];
		const rows = filteredMembers.map(m => `"${m.id}","${m.name}","${m.phone}","${m.districtCode}","${m.platform}","${m.status}","${m.date}"`);
		const csvContent = 'data:text/csv;charset=utf-8,' + [headers, ...rows].join('\n');
		const encodedUri = encodeURI(csvContent);
		const link = document.createElement('a');
		link.setAttribute('href', encodedUri);
		link.setAttribute('download', `ksgpwu_members_export_${new Date().toISOString().slice(0, 10)}.csv`);
		document.body.appendChild(link);
		link.click();
		document.body.removeChild(link);
	}

	function handleLogin() {
		if (authStep === 'cred') {
			if (username === 'state_gs' && password === 'CITUSolidarity@2026') {
				authStep = '2fa';
				authError = '';
			} else {
				authError = 'Invalid credentials. Use state_gs / CITUSolidarity@2026';
			}
		} else {
			if (totp.trim().length >= 6) {
				isLoggedIn = true;
				authError = '';
			} else {
				authError = 'Enter valid 6-8 character 2FA TOTP';
			}
		}
	}

	function handleImportSubmit() {
		importSuccess = true;
		setTimeout(() => {
			importSuccess = false;
			showImportModal = false;
			alert(lang === 'ml' ? 'പേപ്പർ ഫോമുകൾ വിജയകരമായി ഇറക്കുമതി ചെയ്തു.' : 'Paper registration batch imported successfully.');
		}, 1000);
	}
</script>

<svelte:head>
	<title>{lang === 'ml' ? 'അഡ്മിൻ കൺസോൾ | KSGPWU CITU' : 'Admin Console | KSGPWU CITU'}</title>
	<meta name="robots" content="noindex, nofollow, noarchive, nosnippet" />
	<meta name="googlebot" content="noindex, nofollow, noarchive, nosnippet" />
</svelte:head>

{#if !isLoggedIn}
	<!-- Login Screen with 2FA Gate -->
	<div class="min-h-screen bg-[#0F172A] flex items-center justify-center p-4">
		<div class="max-w-md w-full bg-white rounded-2xl shadow-2xl border border-slate-700/50 p-8">
			<div class="text-center mb-6">
				<div class="w-14 h-14 rounded-xl bg-primary text-white mx-auto flex items-center justify-center text-2xl font-bold shadow-md mb-3">
					★
				</div>
				<h2 class="text-xl font-bold text-slate-900">KSGPWU · CITU Admin</h2>
				<p class="text-xs text-slate-500 mt-1">State Executive & District Council Secure Console</p>
			</div>

			{#if authError}
				<div class="mb-4 p-3 bg-red-100 border border-red-300 text-red-800 rounded text-xs flex items-center gap-2">
					<span class="material-symbols-outlined text-[16px]">error</span>
					<span>{authError}</span>
				</div>
			{/if}

			{#if authStep === 'cred'}
				<div class="space-y-4">
					<div>
						<label for="admin-username-input" class="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">Username / ഐഡി</label>
						<input 
							id="admin-username-input"
							type="text" 
							bind:value={username} 
							class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm bg-white text-slate-900 focus:ring-2 focus:ring-primary focus:border-primary outline-none transition"
						/>
					</div>

					<div>
						<label for="admin-password-input" class="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">Password / പാസ്‌വേഡ്</label>
						<input 
							id="admin-password-input"
							type="password" 
							bind:value={password} 
							class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm bg-white text-slate-900 focus:ring-2 focus:ring-primary focus:border-primary outline-none transition"
						/>
					</div>

					<button 
						type="button" 
						onclick={handleLogin}
						class="w-full py-3 bg-primary hover:bg-primary-container text-white font-bold rounded-xl text-sm shadow transition flex items-center justify-center gap-2"
					>
						<span>Continue to 2FA</span>
						<span class="material-symbols-outlined text-[18px]">arrow_forward</span>
					</button>

					<div class="p-2.5 bg-slate-100 rounded-lg text-[11px] text-slate-600 border border-slate-200">
						Demo credentials: <strong>state_gs</strong> / <strong>CITUSolidarity@2026</strong>
					</div>
				</div>
			{:else}
				<div class="space-y-4">
					<div class="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-800 flex items-center gap-2">
						<span class="material-symbols-outlined text-[16px]">lock</span>
						<span>Step 2: Enter 2FA TOTP hardware or authenticator code</span>
					</div>

					<div>
						<label for="admin-totp-input" class="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">TOTP Code / ബാക്കപ്പ് കോഡ്</label>
						<input 
							id="admin-totp-input"
							type="text" 
							bind:value={totp} 
							placeholder="REC001AA"
							class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm text-center font-mono font-bold tracking-widest bg-white text-slate-900 focus:ring-2 focus:ring-primary focus:border-primary outline-none transition"
						/>
					</div>

					<button 
						type="button" 
						onclick={handleLogin}
						class="w-full py-3 bg-primary hover:bg-primary-container text-white font-bold rounded-xl text-sm shadow transition flex items-center justify-center gap-2"
					>
						<span class="material-symbols-outlined text-[18px]">verified_user</span>
						<span>Verify & Authenticate</span>
					</button>

					<div class="p-2.5 bg-slate-100 rounded-lg text-[11px] text-slate-600 border border-slate-200">
						Demo TOTP bypass key: <strong>REC001AA</strong>
					</div>
				</div>
			{/if}
		</div>
	</div>
{:else}
	<!-- Full Executive Dashboard Screen -->
	<div class="min-h-screen bg-surface flex">
		<!-- Left Fixed Sidebar -->
		<aside class="fixed left-0 top-0 h-full w-[260px] bg-[#0F172A] z-50 flex flex-col justify-between text-white shadow-xl">
			<div class="flex flex-col">
				<!-- Union Title & Officer Pill -->
				<div class="p-4 border-b border-slate-800">
					<a href="/" class="flex items-center gap-2.5 group">
						<div class="w-9 h-9 rounded bg-primary-container flex items-center justify-center text-on-primary font-bold text-lg shadow-sm">
							★
						</div>
						<div>
							<div class="text-sm font-bold tracking-tight text-white leading-tight">KSGPWU · CITU</div>
							<div class="text-[11px] text-slate-400 leading-tight mt-0.5">സംസ്ഥാന കമ്മിറ്റി / State HQ</div>
						</div>
					</a>

					<div class="mt-4 p-2.5 rounded bg-slate-800/80 border border-slate-700/60 flex items-center gap-2.5">
						<div class="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-slate-300">
							<span class="material-symbols-outlined text-[18px]">badge</span>
						</div>
						<div class="overflow-hidden">
							<div class="text-xs font-semibold text-slate-200 truncate">Com. K. Balakrishnan</div>
							<div class="text-[10px] text-slate-400 truncate">സംസ്ഥാന സെക്രട്ടറി / Gen. Sec.</div>
						</div>
					</div>
				</div>

				<!-- Nav Links -->
				<nav class="flex flex-col gap-1 p-2">
					<button 
						type="button"
						onclick={() => currentNav = 'overview'}
						class={`w-full flex items-center justify-between px-3 py-2 rounded text-xs transition-colors ${currentNav === 'overview' ? 'bg-primary-container text-on-primary font-semibold shadow-sm' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}
					>
						<div class="flex items-center gap-2.5">
							<span class="material-symbols-outlined text-[18px]">dashboard</span>
							<span>ഡാഷ്‌ബോർഡ് / Overview</span>
						</div>
					</button>

					<button 
						type="button"
						onclick={() => currentNav = 'members'}
						class={`w-full flex items-center justify-between px-3 py-2 rounded text-xs transition-colors ${currentNav === 'members' ? 'bg-primary-container text-on-primary font-semibold shadow-sm' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}
					>
						<div class="flex items-center gap-2.5">
							<span class="material-symbols-outlined text-[18px]">group</span>
							<span>അംഗങ്ങൾ / Members</span>
						</div>
						<span class="text-[10px] px-1.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">42.8k</span>
					</button>

					<button 
						type="button"
						onclick={() => currentNav = 'dues'}
						class={`w-full flex items-center justify-between px-3 py-2 rounded text-xs transition-colors ${currentNav === 'dues' ? 'bg-primary-container text-on-primary font-semibold shadow-sm' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}
					>
						<div class="flex items-center gap-2.5">
							<span class="material-symbols-outlined text-[18px]">payments</span>
							<span>വരിസംഖ്യ / Dues & Fees</span>
						</div>
					</button>

					<button 
						type="button"
						onclick={() => currentNav = 'districts'}
						class={`w-full flex items-center justify-between px-3 py-2 rounded text-xs transition-colors ${currentNav === 'districts' ? 'bg-primary-container text-on-primary font-semibold shadow-sm' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}
					>
						<div class="flex items-center gap-2.5">
							<span class="material-symbols-outlined text-[18px]">account_balance</span>
							<span>ജില്ലകൾ / District Units</span>
						</div>
						<span class="text-[10px] text-slate-400">14</span>
					</button>

					<button 
						type="button"
						onclick={() => currentNav = 'grievances'}
						class={`w-full flex items-center justify-between px-3 py-2 rounded text-xs transition-colors ${currentNav === 'grievances' ? 'bg-primary-container text-on-primary font-semibold shadow-sm' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}
					>
						<div class="flex items-center gap-2.5">
							<span class="material-symbols-outlined text-[18px]">support_agent</span>
							<span>പരാതികൾ / Grievances</span>
						</div>
						<span class="text-[10px] px-1.5 py-0.5 rounded-full bg-primary text-on-primary font-bold">142</span>
					</button>

					<button 
						type="button"
						onclick={() => showImportModal = true}
						class="w-full flex items-center justify-between px-3 py-2 rounded text-xs text-amber-300 hover:bg-slate-800 transition-colors"
					>
						<div class="flex items-center gap-2.5">
							<span class="material-symbols-outlined text-[18px]">upload_file</span>
							<span>പേപ്പർ ഇറക്കുമതി / Bulk Import</span>
						</div>
					</button>

					<button 
						type="button"
						onclick={() => currentNav = 'audit'}
						class={`w-full flex items-center justify-between px-3 py-2 rounded text-xs transition-colors ${currentNav === 'audit' ? 'bg-primary-container text-on-primary font-semibold shadow-sm' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}
					>
						<div class="flex items-center gap-2.5">
							<span class="material-symbols-outlined text-[18px]">history</span>
							<span>ഓഡിറ്റ് ലോഗ് / Audit Log</span>
						</div>
					</button>
				</nav>
			</div>

			<!-- Bottom Security Pill & Logout -->
			<div class="p-4 border-t border-slate-800 flex flex-col gap-2">
				<div class="flex items-center justify-between px-2.5 py-1.5 rounded bg-slate-900 border border-emerald-900/40 text-emerald-400 text-xs">
					<div class="flex items-center gap-1.5">
						<span class="material-symbols-outlined text-[16px]">verified_user</span>
						<span class="text-[11px] font-medium">2FA TOTP Active</span>
					</div>
					<span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
				</div>

				<button 
					type="button" 
					onclick={() => isLoggedIn = false}
					class="flex items-center gap-2 px-2.5 py-2 text-slate-400 hover:text-red-400 text-xs transition-colors"
				>
					<span class="material-symbols-outlined text-[18px]">logout</span>
					<span>ലോഗ് ഔട്ട് / Sign Out</span>
				</button>
			</div>
		</aside>

		<!-- Main Workspace Area -->
		<div class="pl-[260px] w-full min-h-screen flex flex-col bg-slate-50/60">
			<!-- Top Action Bar -->
			<header class="h-16 bg-white/90 backdrop-blur-md border-b border-slate-200/80 z-40 flex items-center justify-between px-6 sticky top-0 shadow-2xs">
				<!-- Search & District Filter -->
				<div class="flex items-center gap-3 flex-1 max-w-2xl">
					<div class="relative w-full max-w-md">
						<span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-[20px]">search</span>
						<input 
							type="text" 
							bind:value={searchQuery}
							placeholder={lang === 'ml' ? 'അംഗത്തെ തിരയുക: പേര്, മൊബൈൽ, ID...' : 'Search member: Name, Phone, ID...'} 
							class="w-full h-10 pl-10 pr-4 bg-slate-100/90 border border-slate-200 rounded-xl text-xs text-slate-800 placeholder:text-slate-400 focus:border-primary focus:bg-white focus:outline-none transition-colors"
						/>
					</div>

					<select 
						bind:value={selectedDistrict}
						class="h-10 px-3 bg-slate-100/90 border border-slate-200 rounded-xl text-xs text-slate-700 font-medium focus:outline-none"
					>
						<option value="All">{lang === 'ml' ? 'എല്ലാ ജില്ലകളും' : 'All 14 Districts'}</option>
						<option value="KLTVC">തിരുവനന്തപുരം (KLTVC)</option>
						<option value="KLKLM">കൊല്ലം (KLKLM)</option>
						<option value="KLERN">എറണാകുളം (KLERN)</option>
						<option value="KLTCR">തൃശ്ശൂർ (KLTCR)</option>
						<option value="KLKZD">കോഴിക്കോട് (KLKZD)</option>
						<option value="KLKTM">കോട്ടയം (KLKTM)</option>
					</select>
				</div>

				<!-- Right Utility Buttons -->
				<div class="flex items-center gap-3">
					<button 
						type="button" 
						onclick={exportCSV}
						class="h-9 px-3.5 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-colors shadow-2xs"
					>
						<span class="material-symbols-outlined text-[18px] text-slate-500">download</span>
						<span>CSV എക്സ്പോർട്ട്</span>
					</button>

					<!-- Language Toggle -->
					<div class="flex rounded-full border border-slate-200 p-0.5 bg-slate-100 text-xs shadow-inner">
						<button 
							type="button" 
							onclick={() => lang = 'ml'}
							class={`px-2.5 py-0.5 rounded-full font-bold transition-all ${lang === 'ml' ? 'bg-primary text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'}`}
						>
							മലയാളം
						</button>
						<button 
							type="button" 
							onclick={() => lang = 'en'}
							class={`px-2.5 py-0.5 rounded-full font-bold transition-all ${lang === 'en' ? 'bg-primary text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'}`}
						>
							EN
						</button>
					</div>

					<!-- Notification Bell -->
					<div class="relative p-2 text-slate-500 hover:text-slate-900 hover:bg-slate-100 rounded-xl transition-colors cursor-pointer">
						<span class="material-symbols-outlined text-[22px]">notifications</span>
						<span class="absolute top-1.5 right-1.5 w-4 h-4 bg-primary text-white rounded-full text-[10px] font-bold flex items-center justify-center leading-none">3</span>
					</div>

					<!-- Admin Profile Avatar -->
					<div class="w-8 h-8 rounded-full bg-gradient-to-br from-red-600 to-red-900 flex items-center justify-center text-white shadow-xs">
						<span class="material-symbols-outlined text-[18px]">person</span>
					</div>
				</div>
			</header>

			<!-- Page Body -->
			<div class="p-6 space-y-6">
				<!-- Context Heading -->
				<div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
					<div>
						<div class="flex items-center gap-1.5 text-slate-500 text-xs font-medium">
							<span>സംസ്ഥാന ആസ്ഥാനം</span>
							<span class="material-symbols-outlined text-[14px]">chevron_right</span>
							<span class="text-slate-900 font-bold">State Executive Overview</span>
						</div>
						<div class="flex items-center gap-2.5 mt-1">
							<h1 class="text-2xl font-black text-slate-900 tracking-tight">
								{lang === 'ml' ? 'ഡാഷ്‌ബോർഡ് അവലോകനം' : 'Executive Console Overview'}
							</h1>
							<span class="text-xs px-3 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-bold border border-emerald-200">Live Cockpit</span>
						</div>
						<div class="flex items-center gap-2 text-slate-500 text-xs mt-1">
							<span class="w-2 h-2 rounded-full bg-emerald-600 animate-pulse"></span>
							<span>Updated 1 min ago · Akshaya Gateway Node-04</span>
						</div>
					</div>

					<div class="flex items-center gap-2.5">
						<button 
							type="button" 
							onclick={() => showImportModal = true}
							class="h-9 px-4 crimson-gradient-btn text-white rounded-xl text-xs font-bold shadow-md flex items-center gap-1.5 transition-all"
						>
							<span class="material-symbols-outlined text-[18px]">upload_file</span>
							<span>{lang === 'ml' ? 'പേപ്പർ ഫോമുകൾ ചേർക്കുക' : 'Bulk Paper Import'}</span>
						</button>
						<a 
							href="/register" 
							target="_blank"
							class="h-9 px-4 bg-white border border-slate-300 hover:bg-slate-50 text-slate-800 rounded-xl text-xs font-bold shadow-xs flex items-center gap-1.5 transition-all"
						>
							<span class="material-symbols-outlined text-[18px] text-slate-500">person_add</span>
							<span>{lang === 'ml' ? 'പുതിയ അപേക്ഷ' : 'New Enrollment'}</span>
						</a>
					</div>
				</div>

				<!-- 4 Metric Cards Grid -->
				<div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
					<!-- Card 1 -->
					<div class="card-gloss rounded-2xl p-5 border border-slate-200/90 shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow">
						<div class="flex items-start justify-between">
							<div class="flex flex-col">
								<span class="text-xs text-slate-500 uppercase font-bold tracking-wider">ആകെ അംഗങ്ങൾ</span>
								<span class="text-[11px] text-slate-400">Total Registered Members</span>
							</div>
							<div class="w-10 h-10 rounded-xl bg-red-100 text-primary flex items-center justify-center shadow-xs">
								<span class="material-symbols-outlined text-[22px]">groups</span>
							</div>
						</div>
						<div class="mt-4">
							<div class="text-3xl font-black text-slate-900">42,850</div>
							<div class="flex items-center gap-1 text-emerald-700 text-xs mt-1">
								<span class="material-symbols-outlined text-[16px]">trending_up</span>
								<span class="font-bold">+184 today</span>
								<span class="text-slate-500">· +4.2% this month</span>
							</div>
						</div>
						<div class="w-full bg-slate-100 h-2 rounded-full overflow-hidden mt-3">
							<div class="bg-primary h-full rounded-full" style="width: 78%"></div>
						</div>
					</div>

					<!-- Card 2 -->
					<div class="card-gloss rounded-2xl p-5 border border-slate-200/90 shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow">
						<div class="flex items-start justify-between">
							<div class="flex flex-col">
								<span class="text-xs text-slate-500 uppercase font-bold tracking-wider">സജീവ വരിസംഖ്യ</span>
								<span class="text-[11px] text-slate-400">Active Dues Compliance</span>
							</div>
							<div class="w-10 h-10 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center shadow-xs">
								<span class="material-symbols-outlined text-[22px]">verified</span>
							</div>
						</div>
						<div class="mt-4">
							<div class="text-3xl font-black text-slate-900">38,420</div>
							<div class="flex items-center gap-1 text-xs mt-1">
								<span class="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-bold text-[10px]">89.6% COMPLIANT</span>
								<span class="text-slate-500">സാധുവായ അംഗത്വം</span>
							</div>
						</div>
						<div class="w-full bg-slate-100 h-2 rounded-full overflow-hidden mt-3">
							<div class="bg-emerald-600 h-full rounded-full" style="width: 89.6%"></div>
						</div>
					</div>

					<!-- Card 3 -->
					<div class="card-gloss rounded-2xl p-5 border border-slate-200/90 shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow">
						<div class="flex items-start justify-between">
							<div class="flex flex-col">
								<span class="text-xs text-slate-500 uppercase font-bold tracking-wider">ഈ മാസത്തെ പിരിവ്</span>
								<span class="text-[11px] text-slate-400">Collections (Oct 2026)</span>
							</div>
							<div class="w-10 h-10 rounded-xl bg-amber-100 text-amber-800 flex items-center justify-center shadow-xs">
								<span class="material-symbols-outlined text-[22px]">account_balance_wallet</span>
							</div>
						</div>
						<div class="mt-4">
							<div class="text-3xl font-black text-slate-900">₹6,84,600</div>
							<div class="text-xs text-slate-500 mt-1">
								<strong class="text-slate-800">98.4%</strong> bank auto-credited via SBT/UPI
							</div>
						</div>
						<div class="w-full bg-slate-100 h-2 rounded-full overflow-hidden mt-3">
							<div class="bg-amber-600 h-full rounded-full" style="width: 98.4%"></div>
						</div>
					</div>

					<!-- Card 4 -->
					<div class="card-gloss rounded-2xl p-5 border border-slate-200/90 shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow">
						<div class="flex items-start justify-between">
							<div class="flex flex-col">
								<span class="text-xs text-slate-500 uppercase font-bold tracking-wider">തുറന്ന പരാതികൾ</span>
								<span class="text-[11px] text-slate-400">Disputes &amp; Conciliations</span>
							</div>
							<div class="w-10 h-10 rounded-xl bg-rose-100 text-rose-800 flex items-center justify-center shadow-xs">
								<span class="material-symbols-outlined text-[22px]">gavel</span>
							</div>
						</div>
						<div class="mt-4">
							<div class="text-3xl font-black text-slate-900">142</div>
							<div class="flex items-center gap-1.5 text-xs mt-1">
								<span class="px-2 py-0.5 rounded-full bg-red-100 text-red-900 font-bold text-[10px]">28 HIGH PRIORITY</span>
								<span class="text-slate-500">14 കൗൺസിലുകൾ</span>
							</div>
						</div>
						<div class="w-full bg-slate-100 h-2 rounded-full overflow-hidden mt-3">
							<div class="bg-primary h-full rounded-full" style="width: 32%"></div>
						</div>
					</div>
				</div>

				<!-- Middle Analytics & Distribution Row -->
				<div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
					<!-- Platform Breakdown (5 cols) -->
					<div class="lg:col-span-5 bg-surface-container-lowest rounded-xl border border-surface-variant p-6 shadow-sm flex flex-col gap-4">
						<div class="flex items-center justify-between pb-2 border-b border-surface-variant">
							<div>
								<h2 class="text-sm font-bold text-on-surface">പ്ലാറ്റ്‌ഫോം വിഹിതം</h2>
								<p class="text-xs text-secondary">Membership Split by Aggregator</p>
							</div>
							<span class="text-xs px-2.5 py-1 rounded bg-surface-container-high text-on-surface font-semibold">42,850 ആകെ</span>
						</div>

						<div class="space-y-3.5 pt-1">
							<!-- Zomato -->
							<div>
								<div class="flex items-center justify-between text-xs mb-1">
									<span class="flex items-center gap-2 font-semibold text-on-surface">
										<span class="w-2.5 h-2.5 rounded-full bg-primary"></span>
										Zomato Delivery Fleet
									</span>
									<span class="font-bold">34% <span class="text-secondary font-normal">(14,569)</span></span>
								</div>
								<div class="w-full bg-surface-container-high h-2 rounded-full overflow-hidden">
									<div class="bg-primary h-full rounded-full" style="width: 34%"></div>
								</div>
							</div>

							<!-- Swiggy -->
							<div>
								<div class="flex items-center justify-between text-xs mb-1">
									<span class="flex items-center gap-2 font-semibold text-on-surface">
										<span class="w-2.5 h-2.5 rounded-full bg-[#EA580C]"></span>
										Swiggy Delivery Associates
									</span>
									<span class="font-bold">28% <span class="text-secondary font-normal">(11,998)</span></span>
								</div>
								<div class="w-full bg-surface-container-high h-2 rounded-full overflow-hidden">
									<div class="bg-[#EA580C] h-full rounded-full" style="width: 28%"></div>
								</div>
							</div>

							<!-- Uber -->
							<div>
								<div class="flex items-center justify-between text-xs mb-1">
									<span class="flex items-center gap-2 font-semibold text-on-surface">
										<span class="w-2.5 h-2.5 rounded-full bg-slate-800"></span>
										Uber Auto &amp; Cab Pilots
									</span>
									<span class="font-bold">16% <span class="text-secondary font-normal">(6,856)</span></span>
								</div>
								<div class="w-full bg-surface-container-high h-2 rounded-full overflow-hidden">
									<div class="bg-slate-800 h-full rounded-full" style="width: 16%"></div>
								</div>
							</div>

							<!-- Rapido -->
							<div>
								<div class="flex items-center justify-between text-xs mb-1">
									<span class="flex items-center gap-2 font-semibold text-on-surface">
										<span class="w-2.5 h-2.5 rounded-full bg-[#D97706]"></span>
										Rapido Bike Taxi &amp; Autos
									</span>
									<span class="font-bold">12% <span class="text-secondary font-normal">(5,142)</span></span>
								</div>
								<div class="w-full bg-surface-container-high h-2 rounded-full overflow-hidden">
									<div class="bg-[#D97706] h-full rounded-full" style="width: 12%"></div>
								</div>
							</div>

							<!-- Logistics -->
							<div>
								<div class="flex items-center justify-between text-xs mb-1">
									<span class="flex items-center gap-2 font-semibold text-on-surface">
										<span class="w-2.5 h-2.5 rounded-full bg-secondary"></span>
										Logistics (Porter, Dunzo, Urban Co)
									</span>
									<span class="font-bold">10% <span class="text-secondary font-normal">(4,285)</span></span>
								</div>
								<div class="w-full bg-surface-container-high h-2 rounded-full overflow-hidden">
									<div class="bg-secondary h-full rounded-full" style="width: 10%"></div>
								</div>
							</div>
						</div>

						<div class="p-2.5 bg-surface-container rounded-lg flex items-center gap-2 text-secondary text-xs mt-2">
							<span class="material-symbols-outlined text-[18px] text-tertiary">cloud_sync</span>
							<span>Automated biometric sync with Kerala Gig Workers Welfare Board (KGWWB) database API.</span>
						</div>
					</div>

					<!-- Districts Summary Ledger (7 cols) -->
					<div class="lg:col-span-7 bg-surface-container-lowest rounded-xl border border-surface-variant p-6 shadow-sm flex flex-col justify-between">
						<div>
							<div class="flex items-center justify-between pb-3 border-b border-surface-variant mb-3">
								<div>
									<h2 class="text-sm font-bold text-on-surface">ജില്ലാ തിരിച്ചുളള കണക്ക്</h2>
									<p class="text-xs text-secondary">District Units Real-Time Density &amp; Dispute Conciliation</p>
								</div>
								<span class="text-xs px-2.5 py-1 rounded bg-secondary-container text-on-secondary-container font-bold">Top 5 Districts</span>
							</div>

							<div class="overflow-x-auto">
								<table class="w-full text-left text-xs">
									<thead>
										<tr class="text-secondary uppercase bg-surface-container-low font-semibold">
											<th class="py-2.5 px-3 rounded-l">ജില്ല / Unit</th>
											<th class="py-2.5 px-3">അംഗങ്ങൾ</th>
											<th class="py-2.5 px-3">വരിസംഖ്യ</th>
											<th class="py-2.5 px-3">പരാതികൾ</th>
											<th class="py-2.5 px-3 text-right rounded-r">പിരിവ്</th>
										</tr>
									</thead>
									<tbody class="divide-y divide-surface-variant text-on-surface">
										<tr class="hover:bg-surface-container-low transition-colors">
											<td class="py-2.5 px-3">
												<div class="font-bold text-on-surface">എറണാകുളം (Ernakulam)</div>
												<div class="text-[10px] text-secondary">KLERN · West Zone HQ</div>
											</td>
											<td class="py-2.5 px-3 font-semibold">9,850</td>
											<td class="py-2.5 px-3 text-emerald-700 font-semibold">91.2%</td>
											<td class="py-2.5 px-3">
												<span class="px-2 py-0.5 rounded-full bg-error-container text-primary font-bold text-[10px]">24 open</span>
											</td>
											<td class="py-2.5 px-3 text-right font-semibold">₹1,57,600</td>
										</tr>
										<tr class="hover:bg-surface-container-low transition-colors">
											<td class="py-2.5 px-3">
												<div class="font-bold text-on-surface">തിരുവനന്തപുരം (Trivandrum)</div>
												<div class="text-[10px] text-secondary">KLTVC · Capital HQ</div>
											</td>
											<td class="py-2.5 px-3 font-semibold">7,420</td>
											<td class="py-2.5 px-3 text-emerald-700 font-semibold">89.5%</td>
											<td class="py-2.5 px-3">
												<span class="px-2 py-0.5 rounded-full bg-surface-container text-secondary font-semibold text-[10px]">18 open</span>
											</td>
											<td class="py-2.5 px-3 text-right font-semibold">₹1,18,720</td>
										</tr>
										<tr class="hover:bg-surface-container-low transition-colors">
											<td class="py-2.5 px-3">
												<div class="font-bold text-on-surface">കോഴിക്കോട് (Kozhikode)</div>
												<div class="text-[10px] text-secondary">KLKKD · Malabar Zone</div>
											</td>
											<td class="py-2.5 px-3 font-semibold">6,110</td>
											<td class="py-2.5 px-3 text-emerald-700 font-semibold">88.4%</td>
											<td class="py-2.5 px-3">
												<span class="px-2 py-0.5 rounded-full bg-surface-container text-secondary font-semibold text-[10px]">15 open</span>
											</td>
											<td class="py-2.5 px-3 text-right font-semibold">₹97,760</td>
										</tr>
										<tr class="hover:bg-surface-container-low transition-colors">
											<td class="py-2.5 px-3">
												<div class="font-bold text-on-surface">തൃശ്ശൂർ (Thrissur)</div>
												<div class="text-[10px] text-secondary">KLTSR · Central Hub</div>
											</td>
											<td class="py-2.5 px-3 font-semibold">4,320</td>
											<td class="py-2.5 px-3 text-emerald-700 font-semibold">90.1%</td>
											<td class="py-2.5 px-3">
												<span class="px-2 py-0.5 rounded-full bg-surface-container text-secondary font-semibold text-[10px]">9 open</span>
											</td>
											<td class="py-2.5 px-3 text-right font-semibold">₹69,120</td>
										</tr>
										<tr class="hover:bg-surface-container-low transition-colors">
											<td class="py-2.5 px-3">
												<div class="font-bold text-on-surface">കൊല്ലം (Kollam)</div>
												<div class="text-[10px] text-secondary">KLKLM · South Coast Hub</div>
											</td>
											<td class="py-2.5 px-3 font-semibold">3,180</td>
											<td class="py-2.5 px-3 text-emerald-700 font-semibold">87.8%</td>
											<td class="py-2.5 px-3">
												<span class="px-2 py-0.5 rounded-full bg-surface-container text-secondary font-semibold text-[10px]">7 open</span>
											</td>
											<td class="py-2.5 px-3 text-right font-semibold">₹50,880</td>
										</tr>
									</tbody>
								</table>
							</div>
						</div>

						<div class="pt-3 border-t border-surface-variant flex items-center justify-between text-xs text-secondary mt-3">
							<span>മൊത്തം 14 ജില്ലകളിലായി 142 കൺസിലിയേഷൻ പരാതികൾ പ്രക്രിയയിലാണ്.</span>
							<button type="button" onclick={() => selectedDistrict = 'All'} class="text-primary font-bold hover:underline flex items-center gap-1">
								<span>14 ജില്ലകളും കാണുക</span>
								<span class="material-symbols-outlined text-[16px]">arrow_forward</span>
							</button>
						</div>
					</div>
				</div>

				<!-- Bottom Member Registration Directory -->
				<div class="bg-surface-container-lowest rounded-xl border border-surface-variant shadow-sm overflow-hidden">
					<!-- Table Header Filters -->
					<div class="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-surface-variant">
						<div>
							<h2 class="text-base font-bold text-on-surface">സമീപകാല രജിസ്ട്രേഷനുകൾ</h2>
							<p class="text-xs text-secondary">തത്സമയ അപേക്ഷകളും അംഗത്വ സ്ഥിരീകരണവും / Realtime verification ledger</p>
						</div>

						<!-- Segmented Filters -->
						<div class="flex items-center p-1 bg-surface-container rounded-lg text-xs gap-1">
							<button 
								type="button" 
								onclick={() => selectedCategory = 'all'} 
								class={`px-3 py-1.5 rounded-md font-semibold transition-all ${selectedCategory === 'all' ? 'bg-primary text-on-primary shadow-sm' : 'text-secondary hover:text-on-surface'}`}
							>
								എല്ലാം / All
							</button>
							<button 
								type="button" 
								onclick={() => selectedCategory = 'delivery'} 
								class={`px-3 py-1.5 rounded-md font-semibold transition-all ${selectedCategory === 'delivery' ? 'bg-primary text-on-primary shadow-sm' : 'text-secondary hover:text-on-surface'}`}
							>
								ഡെലിവറി / Delivery
							</button>
							<button 
								type="button" 
								onclick={() => selectedCategory = 'ride'} 
								class={`px-3 py-1.5 rounded-md font-semibold transition-all ${selectedCategory === 'ride' ? 'bg-primary text-on-primary shadow-sm' : 'text-secondary hover:text-on-surface'}`}
							>
								റൈഡ് / Ride
							</button>
							<button 
								type="button" 
								onclick={() => selectedCategory = 'services'} 
								class={`px-3 py-1.5 rounded-md font-semibold transition-all ${selectedCategory === 'services' ? 'bg-primary text-on-primary shadow-sm' : 'text-secondary hover:text-on-surface'}`}
							>
								മറ്റുള്ളവ / Services
							</button>
						</div>
					</div>

					<!-- Table -->
					<div class="overflow-x-auto">
						<table class="w-full text-left text-xs">
							<thead class="bg-surface-container-low text-secondary uppercase font-semibold">
								<tr>
									<th class="py-3 px-5">അംഗത്വ നമ്പർ / ID</th>
									<th class="py-3 px-4">തൊഴിലാളി പേര് / Member</th>
									<th class="py-3 px-4">ജില്ല / District</th>
									<th class="py-3 px-4">പ്ലാറ്റ്‌ഫോം / Platform</th>
									<th class="py-3 px-4">രജിസ്ട്രേഷൻ തീയതി</th>
									<th class="py-3 px-4">സ്റ്റാറ്റസ് / Status</th>
									<th class="py-3 px-5 text-right">നടപടികൾ / Actions</th>
								</tr>
							</thead>
							<tbody class="divide-y divide-surface-variant text-on-surface">
								{#each filteredMembers as member}
									<tr class="hover:bg-surface-container-low transition-colors">
										<td class="py-3.5 px-5 font-mono text-primary font-bold">
											{member.id}
										</td>
										<td class="py-3.5 px-4">
											<div class="flex items-center gap-2.5">
												<div class="w-8 h-8 rounded-full bg-surface-container-high flex items-center justify-center font-bold text-on-surface text-xs">
													{member.avatar}
												</div>
												<div>
													<div class="font-bold text-on-surface leading-tight">{member.name}</div>
													<div class="text-[11px] text-secondary">{member.role}</div>
												</div>
											</div>
										</td>
										<td class="py-3.5 px-4 font-medium text-secondary">
											{member.district}
										</td>
										<td class="py-3.5 px-4">
											<span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-surface-container text-on-surface border border-surface-variant">
												{member.platform}
											</span>
										</td>
										<td class="py-3.5 px-4 text-secondary">
											{member.date}
										</td>
										<td class="py-3.5 px-4">
											{#if member.status === 'active'}
												<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-bold">
													<span class="material-symbols-outlined text-[13px]">check_circle</span>
													സജീവം / Active
												</span>
											{:else}
												<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-100 text-amber-900 text-[10px] font-bold">
													<span class="material-symbols-outlined text-[13px]">hourglass_empty</span>
													പെൻഡിംഗ് / Pending
												</span>
											{/if}
										</td>
										<td class="py-3.5 px-5 text-right">
											<div class="flex items-center justify-end gap-1.5">
												<a 
													href={`/verify/${member.id}`} 
													class="px-2.5 py-1 rounded bg-surface-container text-on-surface font-semibold hover:bg-surface-container-high transition-colors flex items-center gap-1 text-[11px]"
												>
													<span class="material-symbols-outlined text-[15px]">badge</span>
													<span>ഐഡി കാർഡ്</span>
												</a>
												<button 
													type="button" 
													onclick={() => selectedMemberForModal = member}
													class="px-2.5 py-1 rounded bg-surface-container text-on-surface font-semibold hover:bg-surface-container-high transition-colors text-[11px]"
												>
													വിശദാംശങ്ങൾ
												</button>
											</div>
										</td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>

					<!-- Table Pagination Footer -->
					<div class="p-4 flex flex-col md:flex-row md:items-center justify-between gap-3 border-t border-surface-variant text-xs text-secondary">
						<div>
							Showing <strong class="text-on-surface">1–{filteredMembers.length}</strong> of <strong class="text-on-surface">42,850</strong> members
						</div>
						<div class="flex items-center gap-1">
							<button class="px-2.5 py-1 rounded bg-surface-container-high text-secondary opacity-60 cursor-not-allowed" disabled>
								മുൻപത്തെ
							</button>
							<button class="w-7 h-7 rounded bg-primary text-on-primary font-bold">1</button>
							<button class="w-7 h-7 rounded bg-surface-container text-on-surface hover:bg-surface-container-high">2</button>
							<button class="w-7 h-7 rounded bg-surface-container text-on-surface hover:bg-surface-container-high">3</button>
							<span class="px-1 text-secondary">...</span>
							<button class="px-2.5 py-1 rounded bg-surface-container hover:bg-surface-container-high text-on-surface">
								അടുത്തത്
							</button>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
{/if}

<!-- Bulk Import Modal -->
{#if showImportModal}
	<div class="fixed inset-0 z-50 bg-slate-950/75 backdrop-blur-sm flex items-center justify-center p-4">
		<div class="bg-white max-w-lg w-full rounded-2xl shadow-2xl border border-slate-200 p-6 sm:p-7 relative z-10">
			<div class="flex items-center justify-between pb-3.5 border-b border-slate-100 mb-4">
				<div class="flex items-center gap-2.5">
					<div class="w-9 h-9 rounded-xl bg-red-50 text-primary flex items-center justify-center">
						<span class="material-symbols-outlined text-2xl">upload_file</span>
					</div>
					<div>
						<h3 class="text-base font-bold text-slate-900">പേപ്പർ ഫോമുകൾ ബൾക്ക് ഇംപോർട്ട് (CSV)</h3>
						<p class="text-[11px] text-slate-500">Offline Membership Forms Bulk Ingestion</p>
					</div>
				</div>
				<button 
					type="button" 
					onclick={() => showImportModal = false}
					class="w-8 h-8 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 flex items-center justify-center transition-colors"
					aria-label="Close modal"
				>
					<span class="material-symbols-outlined text-[20px]">close</span>
				</button>
			</div>

			<div class="space-y-4 text-xs">
				<p class="text-slate-600 leading-relaxed bg-slate-50 p-3 rounded-xl border border-slate-100">
					യൂണിയൻ ക്യാമ്പുകളിൽ നിന്നും ശേഖരിച്ച പേപ്പർ രജിസ്ട്രേഷൻ അപേക്ഷകൾ CSV ഫയൽ വഴി അപ്‌ലോഡ് ചെയ്യുക. ഡ്യൂപ്ലിക്കേഷൻ സ്വയമേവ പരിശോധിച്ച് റിപ്പോർട്ട് ലഭ്യമാക്കും.
				</p>

				<div>
					<label for="import-district-select" class="block font-bold uppercase text-[11px] tracking-wider text-slate-600 mb-1.5">ജില്ല / District Unit</label>
					<select 
						id="import-district-select"
						bind:value={importDistrict} 
						class="w-full h-10 px-3 rounded-xl border border-slate-300 bg-white text-slate-800 font-medium focus:ring-2 focus:ring-primary focus:border-primary outline-none transition"
					>
						<option value="KLERN">Ernakulam (എറണാകുളം) [KLERN]</option>
						<option value="KLTVC">Thiruvananthapuram (തിരുവനന്തപുരം) [KLTVC]</option>
						<option value="KLKKD">Kozhikode (കോഴിക്കോട്) [KLKKD]</option>
						<option value="KLTSR">Thrissur (തൃശ്ശൂർ) [KLTSR]</option>
					</select>
				</div>

				<div>
					<label for="import-collector-input" class="block font-bold uppercase text-[11px] tracking-wider text-slate-600 mb-1.5">ശേഖരിച്ച ഭാരവാഹിയുടെ പേര് / Unit Collector</label>
					<input 
						id="import-collector-input"
						type="text" 
						bind:value={importCollector} 
						placeholder="ഉദാ: Com. K. Balakrishnan"
						class="w-full h-10 px-3 rounded-xl border border-slate-300 bg-white text-slate-800 font-medium focus:ring-2 focus:ring-primary focus:border-primary outline-none transition"
					/>
				</div>

				<div class="p-6 border-2 border-dashed border-slate-300 rounded-2xl text-center bg-slate-50 hover:bg-slate-100/70 transition-colors">
					<div class="w-12 h-12 rounded-full bg-red-50 text-primary mx-auto flex items-center justify-center mb-2 shadow-xs">
						<span class="material-symbols-outlined text-2xl">file_upload</span>
					</div>
					<div class="font-bold text-slate-900 text-sm">CSV ഫയൽ തിരഞ്ഞെടുക്കുക</div>
					<div class="text-[11px] text-slate-500 mt-1">Columns: FullName, Phone, DOB, Gender, Platform, Last4ID</div>
					<input 
						type="file" 
						accept=".csv" 
						class="mt-3 text-xs text-slate-600 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-primary file:text-white hover:file:bg-primary-container cursor-pointer" 
						onchange={(e) => {
							const t = e.target as HTMLInputElement;
							if (t.files) importFile = t.files[0];
						}}
					/>
				</div>

				<div class="flex justify-end gap-2.5 pt-3 border-t border-slate-100">
					<button 
						type="button" 
						onclick={() => showImportModal = false}
						class="px-4 py-2.5 border border-slate-300 rounded-xl text-slate-600 hover:bg-slate-100 font-semibold transition"
					>
						റദ്ദാക്കുക
					</button>
					<button 
						type="button" 
						onclick={handleImportSubmit}
						class="px-5 py-2.5 bg-primary hover:bg-primary-container text-white font-bold rounded-xl shadow-md transition"
					>
						ഇംപോർട്ട് ആരംഭിക്കുക
					</button>
				</div>
			</div>
		</div>
	</div>
{/if}

<!-- Member Detail Modal -->
{#if selectedMemberForModal}
	<div class="fixed inset-0 z-50 bg-slate-950/75 backdrop-blur-sm flex items-center justify-center p-4">
		<div class="bg-white max-w-md w-full rounded-2xl shadow-2xl border border-slate-200 p-6 sm:p-7 relative z-10">
			<div class="flex items-center justify-between pb-3.5 border-b border-slate-100 mb-4">
				<div class="flex items-center gap-2.5">
					<div class="w-9 h-9 rounded-xl bg-red-50 text-primary flex items-center justify-center">
						<span class="material-symbols-outlined text-2xl">badge</span>
					</div>
					<div>
						<h3 class="text-base font-bold text-slate-900">അംഗത്വ വിവരങ്ങൾ</h3>
						<p class="text-[11px] text-slate-500">Official Member Record</p>
					</div>
				</div>
				<button 
					type="button" 
					onclick={() => selectedMemberForModal = null}
					class="w-8 h-8 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 flex items-center justify-center transition-colors"
					aria-label="Close modal"
				>
					<span class="material-symbols-outlined text-[20px]">close</span>
				</button>
			</div>

			<div class="space-y-3 text-xs bg-slate-50 p-4 rounded-xl border border-slate-100">
				<div class="flex justify-between py-1.5 border-b border-slate-200/60">
					<span class="text-slate-500 font-medium">അംഗത്വ നമ്പർ:</span>
					<span class="font-mono font-bold text-primary">{selectedMemberForModal.id}</span>
				</div>
				<div class="flex justify-between py-1.5 border-b border-slate-200/60">
					<span class="text-slate-500 font-medium">പേര്:</span>
					<span class="font-bold text-slate-900">{selectedMemberForModal.name}</span>
				</div>
				<div class="flex justify-between py-1.5 border-b border-slate-200/60">
					<span class="text-slate-500 font-medium">മൊബൈൽ നമ്പർ:</span>
					<span class="font-mono text-slate-800">{selectedMemberForModal.phone}</span>
				</div>
				<div class="flex justify-between py-1.5 border-b border-slate-200/60">
					<span class="text-slate-500 font-medium">ജില്ല:</span>
					<span class="text-slate-800">{selectedMemberForModal.district}</span>
				</div>
				<div class="flex justify-between py-1.5 border-b border-slate-200/60">
					<span class="text-slate-500 font-medium">പ്ലാറ്റ്‌ഫോം:</span>
					<span class="font-semibold text-primary">{selectedMemberForModal.platform}</span>
				</div>
				<div class="flex justify-between py-1.5">
					<span class="text-slate-500 font-medium">വരിസംഖ്യ സാധുത:</span>
					<span class="text-emerald-700 font-bold">{selectedMemberForModal.paidUpTo}</span>
				</div>
			</div>

			<div class="pt-4 flex gap-2.5">
				<a 
					href={`/verify/${selectedMemberForModal.id}`} 
					class="flex-1 py-2.5 rounded-xl bg-primary text-white text-center font-bold text-xs shadow-md hover:bg-primary-container transition"
				>
					ഡിജിറ്റൽ കാർഡ് കാണുക
				</a>
				<button 
					type="button" 
					onclick={() => selectedMemberForModal = null}
					class="px-4 py-2.5 rounded-xl border border-slate-300 text-slate-700 text-xs font-semibold hover:bg-slate-100 transition"
				>
					അടയ്ക്കുക
				</button>
			</div>
		</div>
	</div>
{/if}
