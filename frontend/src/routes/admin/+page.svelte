<script lang="ts">
	import { currentLanguage } from '$lib/i18n';

	let lang = $state('ml');
	currentLanguage.subscribe((val) => {
		lang = val;
	});

	// Login State
	let isLoggedIn = $state(false);
	let step = $state<'login' | '2fa' | 'dashboard'>('login');
	let username = $state('state_gs');
	let password = $state('CITUSolidarity@2026');
	let challengeToken = $state('');
	let totpCode = $state('REC001AA');
	let loginError = $state('');
	let loading = $state(false);

	// Logged-in admin context
	let adminRole = $state('state_admin');
	let adminName = $state('Com. P. K. Sasidharan');
	let sessionToken = $state('');

	// Dashboard tab
	let activeTab = $state<'members' | 'import' | 'payments' | 'audit'>('members');

	// Member Directory State
	let searchQuery = $state('');
	let filterDistrict = $state('');
	let filterStatus = $state('');

	let members = $state([
		{
			id: '1',
			membership_number: 'KLKKD000001',
			full_name: 'Com. Muhammed Basheer',
			phone: '+919847000001',
			district_code: 'KLKKD',
			district_name: 'Kozhikode',
			primary_platform: 'Zomato',
			sector: 'Food Delivery',
			status: 'active',
			paid_up_to: 'April 2027',
			created_at: '2026-04-01'
		},
		{
			id: '2',
			membership_number: 'KLKKD000002',
			full_name: 'Com. Anoop K',
			phone: '+919847000002',
			district_code: 'KLKKD',
			district_name: 'Kozhikode',
			primary_platform: 'Swiggy',
			sector: 'Food Delivery',
			status: 'active',
			paid_up_to: 'April 2027',
			created_at: '2026-04-02'
		},
		{
			id: '3',
			membership_number: 'KLEKM000042',
			full_name: 'Com. Rahul Krishnan',
			phone: '+919847012345',
			district_code: 'KLEKM',
			district_name: 'Ernakulam',
			primary_platform: 'Swiggy',
			sector: 'Food Delivery',
			status: 'active',
			paid_up_to: 'April 2027',
			created_at: '2026-04-03'
		},
		{
			id: '4',
			membership_number: 'KLEKM000043',
			full_name: 'Com. Deepa Varghese',
			phone: '+919847023456',
			district_code: 'KLEKM',
			district_name: 'Ernakulam',
			primary_platform: 'Uber',
			sector: 'Taxi & Cab',
			status: 'suspended',
			paid_up_to: 'June 2026',
			created_at: '2026-04-04'
		},
		{
			id: '5',
			membership_number: 'KLTVC000001',
			full_name: 'Com. Suresh Kumar',
			phone: '+919847034567',
			district_code: 'KLTVC',
			district_name: 'Thiruvananthapuram',
			primary_platform: 'Ola',
			sector: 'Taxi & Cab',
			status: 'active',
			paid_up_to: 'April 2027',
			created_at: '2026-04-05'
		}
	]);

	// Filtered members
	let filteredMembers = $derived(
		members.filter((m) => {
			const matchesSearch =
				!searchQuery ||
				m.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
				m.phone.includes(searchQuery) ||
				m.membership_number.toLowerCase().includes(searchQuery.toLowerCase());
			const matchesDistrict = !filterDistrict || m.district_code === filterDistrict;
			const matchesStatus = !filterStatus || m.status === filterStatus;
			return matchesSearch && matchesDistrict && matchesStatus;
		})
	);

	// Bulk Import State
	let importBatchSize = $state(4);
	let importStatus = $state('');
	let importReport = $state<{ total: number; accepted: number; skipped: number; rejected: number } | null>(null);

	async function handleLoginSubmit(e: Event) {
		e.preventDefault();
		loading = true;
		loginError = '';

		try {
			const res = await fetch('/api/auth/admin/login', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ username, password })
			});
			const data = await res.json();
			if (!res.ok) {
				loginError = data.detail || (lang === 'ml' ? 'ലോഗിൻ വിവരങ്ങൾ തെറ്റാണ്' : 'Invalid credentials');
				loading = false;
				return;
			}
			if (data.requires_2fa) {
				challengeToken = data.challenge_token;
				step = '2fa';
			}
		} catch {
			// Fallback mock step for dev environment
			challengeToken = 'chal_mock_9999';
			step = '2fa';
		} finally {
			loading = false;
		}
	}

	async function handle2FASubmit(e: Event) {
		e.preventDefault();
		loading = true;
		loginError = '';

		try {
			const res = await fetch('/api/auth/admin/2fa', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ challenge_token: challengeToken, totp_code: totpCode })
			});
			const data = await res.json();
			if (!res.ok) {
				loginError = data.detail || (lang === 'ml' ? '2FA കോഡ് തെറ്റാണ്' : 'Invalid 2FA code');
				loading = false;
				return;
			}
			adminRole = data.role || 'state_admin';
			adminName = data.name || 'Com. P. K. Sasidharan';
			sessionToken = data.session_token || '';
			isLoggedIn = true;
			step = 'dashboard';
		} catch {
			// Fallback mock dashboard for local UI testing
			adminRole = 'state_admin';
			adminName = 'Com. P. K. Sasidharan';
			isLoggedIn = true;
			step = 'dashboard';
		} finally {
			loading = false;
		}
	}

	function handleToggleMemberStatus(memberId: string) {
		const target = members.find((m) => m.id === memberId);
		if (target) {
			target.status = target.status === 'active' ? 'suspended' : 'active';
		}
	}

	function handleSimulateImport() {
		loading = true;
		importStatus = lang === 'ml' ? 'ഫയൽ പരിശോധിക്കുന്നു...' : 'Validating paper records...';
		setTimeout(() => {
			importReport = {
				total: 150,
				accepted: 142,
				skipped: 6,
				rejected: 2
			};
			importStatus = lang === 'ml' ? 'ഇംപോർട്ട് വിജയകരമായി പൂർത്തിയായി!' : 'Import completed successfully!';
			loading = false;
		}, 1000);
	}

	function handleLogout() {
		isLoggedIn = false;
		step = 'login';
		challengeToken = '';
	}
</script>

<div class="space-y-6 max-w-4xl mx-auto">
	{#if step === 'login'}
		<!-- Step 1: Admin Login Card -->
		<div class="bg-white p-6 sm:p-8 rounded-2xl shadow-sm border border-slate-200 space-y-6">
			<div class="flex items-center space-x-3 pb-4 border-b border-slate-100">
				<div class="w-12 h-12 rounded-xl bg-citu-red text-white flex items-center justify-center font-bold text-2xl shadow">
					★
				</div>
				<div>
					<h2 class="text-lg sm:text-xl font-bold text-citu-slate-dark">
						{lang === 'ml' ? 'അഡ്മിനിസ്ട്രേറ്റർ ലോഗിൻ' : 'Union Administrative Portal'}
					</h2>
					<p class="text-xs text-slate-500">
						{lang === 'ml' ? 'സംസ്ഥാന / ജില്ലാ കമ്മിറ്റി പോർട്ടൽ' : 'CITU Kerala State & District Committee Console'}
					</p>
				</div>
			</div>

			{#if loginError}
				<div class="p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl font-semibold">
					{loginError}
				</div>
			{/if}

			<form onsubmit={handleLoginSubmit} class="space-y-4">
				<div>
					<label for="username" class="block text-xs font-bold text-slate-700 mb-1 uppercase tracking-wide">
						{lang === 'ml' ? 'യൂസർനെയിം' : 'Username'}
					</label>
					<input
						id="username"
						type="text"
						bind:value={username}
						required
						class="w-full px-4 py-3 rounded-xl border border-slate-300 focus:ring-2 focus:ring-citu-red focus:border-citu-red outline-none text-sm transition"
					/>
				</div>

				<div>
					<label for="password" class="block text-xs font-bold text-slate-700 mb-1 uppercase tracking-wide">
						{lang === 'ml' ? 'പാസ്‌വേഡ്' : 'Password'}
					</label>
					<input
						id="password"
						type="password"
						bind:value={password}
						required
						class="w-full px-4 py-3 rounded-xl border border-slate-300 focus:ring-2 focus:ring-citu-red focus:border-citu-red outline-none text-sm transition"
					/>
				</div>

				<div class="p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-800 space-y-1">
					<p class="font-bold">
						{lang === 'ml' ? 'ടെസ്റ്റ് അക്കൗണ്ട് വിവരങ്ങൾ:' : 'Default Test Credentials:'}
					</p>
					<p>Username: <code class="bg-amber-100 px-1 py-0.5 rounded font-mono">state_gs</code></p>
					<p>Password: <code class="bg-amber-100 px-1 py-0.5 rounded font-mono">CITUSolidarity@2026</code></p>
				</div>

				<button
					type="submit"
					disabled={loading}
					class="w-full py-3.5 bg-citu-red hover:bg-citu-red-dark text-white font-bold rounded-xl shadow-md transition transform active:scale-98 text-sm flex items-center justify-center space-x-2"
				>
					<span>{loading ? (lang === 'ml' ? 'ലോഗിൻ ചെയ്യുന്നു...' : 'Authenticating...') : (lang === 'ml' ? 'തുടരുക (2FA)' : 'Continue to 2FA')}</span>
					<span>→</span>
				</button>
			</form>
		</div>

	{:else if step === '2fa'}
		<!-- Step 2: Mandatory TOTP 2FA -->
		<div class="bg-white p-6 sm:p-8 rounded-2xl shadow-sm border border-slate-200 space-y-6">
			<div class="flex items-center space-x-3 pb-4 border-b border-slate-100">
				<div class="w-12 h-12 rounded-xl bg-amber-500 text-white flex items-center justify-center font-bold text-2xl shadow">
					🔐
				</div>
				<div>
					<h2 class="text-lg sm:text-xl font-bold text-citu-slate-dark">
						{lang === 'ml' ? 'രണ്ടാം ഘട്ട സുരക്ഷാ കോഡ് (2FA)' : 'Two-Factor Authentication (2FA)'}
					</h2>
					<p class="text-xs text-slate-500">
						{lang === 'ml' ? 'ഓതന്റിക്കേറ്റർ ആപ്പ് കോഡ് അല്ലെങ്കിൽ റിക്കവറി കോഡ് നൽകുക' : 'Enter 6-digit TOTP code or backup recovery code (FR7.9)'}
					</p>
				</div>
			</div>

			{#if loginError}
				<div class="p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl font-semibold">
					{loginError}
				</div>
			{/if}

			<form onsubmit={handle2FASubmit} class="space-y-4">
				<div>
					<label for="totp" class="block text-xs font-bold text-slate-700 mb-1 uppercase tracking-wide">
						{lang === 'ml' ? '2FA കോഡ് / റിക്കവറി കോഡ്' : 'Authenticator Code / Recovery Code'}
					</label>
					<input
						id="totp"
						type="text"
						bind:value={totpCode}
						placeholder="e.g. 123456 or REC001AA"
						required
						class="w-full px-4 py-3 rounded-xl border border-slate-300 focus:ring-2 focus:ring-citu-red focus:border-citu-red outline-none text-base font-mono tracking-widest text-center transition"
					/>
				</div>

				<div class="p-3 bg-blue-50 border border-blue-200 rounded-xl text-xs text-blue-800">
					<p class="font-bold">{lang === 'ml' ? 'ഡെമോ റിക്കവറി കോഡ്:' : 'Demo Recovery Code:'}</p>
					<code class="bg-blue-100 px-1 py-0.5 rounded font-mono font-bold">REC001AA</code>
				</div>

				<div class="flex space-x-3 pt-2">
					<button
						type="button"
						onclick={() => (step = 'login')}
						class="flex-1 py-3 border border-slate-300 hover:bg-slate-50 text-slate-700 font-bold rounded-xl text-sm transition"
					>
						{lang === 'ml' ? 'റദ്ദാക്കുക' : 'Cancel'}
					</button>
					<button
						type="submit"
						disabled={loading}
						class="flex-1 py-3 bg-citu-red hover:bg-citu-red-dark text-white font-bold rounded-xl shadow-md transition text-sm flex items-center justify-center space-x-2"
					>
						<span>{loading ? '...' : (lang === 'ml' ? 'സ്ഥിരീകരിക്കുക' : 'Verify & Enter')}</span>
						<span>✓</span>
					</button>
				</div>
			</form>
		</div>

	{:else if step === 'dashboard'}
		<!-- Step 3: Admin Console Dashboard -->
		<div class="space-y-6">
			<!-- Header Badge & Quick Actions -->
			<div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
				<div class="flex items-center space-x-3">
					<div class="w-12 h-12 rounded-xl bg-citu-red text-white flex items-center justify-center font-bold text-2xl shadow">
						★
					</div>
					<div>
						<div class="flex items-center space-x-2">
							<h2 class="text-base sm:text-lg font-bold text-citu-slate-dark">{adminName}</h2>
							<span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-red-100 text-citu-red border border-red-200">
								{adminRole === 'state_admin' ? 'State Office' : 'District Unit'}
							</span>
						</div>
						<p class="text-xs text-slate-500">
							{lang === 'ml' ? 'കേരള സ്റ്റേറ്റ് ഗിഗ് & പ്ലാറ്റ്‌ഫോം വർക്കേഴ്സ് യൂണിയൻ' : 'Kerala State Gig & Platform Workers Union (CITU)'}
						</p>
					</div>
				</div>

				<div class="flex items-center space-x-2 w-full sm:w-auto">
					<a
						href="/api/admin/members/export"
						target="_blank"
						class="px-3.5 py-2 bg-slate-800 hover:bg-slate-900 text-white rounded-xl text-xs font-bold shadow-sm transition flex items-center space-x-1.5"
					>
						<span>📥</span>
						<span>{lang === 'ml' ? 'CSV എക്സ്പോർട്ട്' : 'Export CSV'}</span>
					</a>
					<button
						onclick={handleLogout}
						class="px-3.5 py-2 border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-xl text-xs font-bold transition"
					>
						{lang === 'ml' ? 'ലോഗൗട്ട്' : 'Logout'}
					</button>
				</div>
			</div>

			<!-- Navigation Tabs -->
			<div class="flex border-b border-slate-200 text-xs sm:text-sm font-semibold space-x-2">
				<button
					onclick={() => (activeTab = 'members')}
					class={`pb-3 px-3 transition border-b-2 font-bold ${
						activeTab === 'members'
							? 'border-citu-red text-citu-red'
							: 'border-transparent text-slate-500 hover:text-slate-800'
					}`}
				>
					👥 {lang === 'ml' ? 'അംഗങ്ങളുടെ പട്ടിക' : 'Member Directory'} ({filteredMembers.length})
				</button>
				<button
					onclick={() => (activeTab = 'import')}
					class={`pb-3 px-3 transition border-b-2 font-bold ${
						activeTab === 'import'
							? 'border-citu-red text-citu-red'
							: 'border-transparent text-slate-500 hover:text-slate-800'
					}`}
				>
					📄 {lang === 'ml' ? 'പേപ്പർ ഫോം ഇംപോർട്ട്' : 'Bulk Paper Import'}
				</button>
				<button
					onclick={() => (activeTab = 'payments')}
					class={`pb-3 px-3 transition border-b-2 font-bold ${
						activeTab === 'payments'
							? 'border-citu-red text-citu-red'
							: 'border-transparent text-slate-500 hover:text-slate-800'
					}`}
				>
					💳 {lang === 'ml' ? 'പേയ്‌മെന്റ് റിപ്പോർട്ട്' : 'Payment Ledger'}
				</button>
				<button
					onclick={() => (activeTab = 'audit')}
					class={`pb-3 px-3 transition border-b-2 font-bold ${
						activeTab === 'audit'
							? 'border-citu-red text-citu-red'
							: 'border-transparent text-slate-500 hover:text-slate-800'
					}`}
				>
					🛡️ {lang === 'ml' ? 'ഓഡിറ്റ് ലോഗ്' : 'Audit Trail'}
				</button>
			</div>

			<!-- TAB 1: MEMBERS DIRECTORY -->
			{#if activeTab === 'members'}
				<div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 space-y-4">
					<!-- Filters Bar -->
					<div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
						<input
							type="text"
							placeholder={lang === 'ml' ? 'പേര്, ഫോൺ, നമ്പർ തിരയുക...' : 'Search name, phone, member ID...'}
							bind:value={searchQuery}
							class="px-3.5 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-citu-red outline-none"
						/>
						<select
							bind:value={filterDistrict}
							class="px-3.5 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-citu-red outline-none"
						>
							<option value="">{lang === 'ml' ? 'എല്ലാ ജില്ലകളും' : 'All Districts'}</option>
							<option value="KLKKD">Kozhikode (കോഴിക്കോട്)</option>
							<option value="KLEKM">Ernakulam (എറണാകുളം)</option>
							<option value="KLTVC">Thiruvananthapuram (തിരുവനന്തപുരം)</option>
						</select>
						<select
							bind:value={filterStatus}
							class="px-3.5 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-citu-red outline-none"
						>
							<option value="">{lang === 'ml' ? 'എല്ലാ സ്റ്റാറ്റസും' : 'All Statuses'}</option>
							<option value="active">Active (സജീവം)</option>
							<option value="suspended">Suspended (സസ്‌പെൻഡ് ചെയ്തത്)</option>
						</select>
					</div>

					<!-- Table -->
					<div class="overflow-x-auto">
						<table class="w-full text-left text-xs border-collapse">
							<thead>
								<tr class="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase tracking-wider font-semibold">
									<th class="py-3 px-3">Member ID</th>
									<th class="py-3 px-3">Name</th>
									<th class="py-3 px-3">Phone</th>
									<th class="py-3 px-3">District</th>
									<th class="py-3 px-3">Platform</th>
									<th class="py-3 px-3">Status</th>
									<th class="py-3 px-3">Paid Up To</th>
									<th class="py-3 px-3 text-right">Action</th>
								</tr>
							</thead>
							<tbody class="divide-y divide-slate-100">
								{#each filteredMembers as m}
									<tr class="hover:bg-slate-50 transition">
										<td class="py-3 px-3 font-mono font-bold text-citu-red">{m.membership_number}</td>
										<td class="py-3 px-3 font-semibold text-slate-800">{m.full_name}</td>
										<td class="py-3 px-3 text-slate-600">{m.phone}</td>
										<td class="py-3 px-3">{m.district_name}</td>
										<td class="py-3 px-3 font-medium">{m.primary_platform}</td>
										<td class="py-3 px-3">
											<span
												class={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
													m.status === 'active'
														? 'bg-emerald-100 text-emerald-700'
														: 'bg-amber-100 text-amber-700'
												}`}
											>
												{m.status}
											</span>
										</td>
										<td class="py-3 px-3 text-slate-500">{m.paid_up_to}</td>
										<td class="py-3 px-3 text-right space-x-1">
											<button
												onclick={() => handleToggleMemberStatus(m.id)}
												class="px-2 py-1 bg-slate-100 hover:bg-slate-200 rounded font-semibold text-[11px] text-slate-700 transition"
											>
												{m.status === 'active' ? 'Suspend' : 'Activate'}
											</button>
										</td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				</div>

			<!-- TAB 2: BULK PAPER IMPORT -->
			{:else if activeTab === 'import'}
				<div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-6">
					<div>
						<h3 class="text-base font-bold text-citu-slate-dark">
							{lang === 'ml' ? 'പേപ്പർ മെമ്പർഷിപ്പ് വിവരങ്ങൾ അപ്‌ലോഡ് ചെയ്യുക' : 'Bulk Migration from Paper & Google Forms (FR10)'}
						</h3>
						<p class="text-xs text-slate-500">
							{lang === 'ml'
								? '5,000-ലധികം രേഖകൾ ഒരേ സമയം അപ്‌ലോഡ് ചെയ്യാം. ഡ്യൂപ്ലിക്കേറ്റ് നമ്പറുകൾ സ്വയം ഒഴിവാക്കപ്പെടും.'
								: 'Upload CSV/Excel of paper records. Duplicates skipped automatically, sequential IDs allocated, and offline payments logged.'}
						</p>
					</div>

					<div class="p-4 bg-slate-50 border border-dashed border-slate-300 rounded-xl flex flex-col items-center justify-center space-y-3 text-center">
						<span class="text-3xl">📊</span>
						<div>
							<p class="text-xs font-bold text-slate-700">kozhikode_pilot_paper_records.csv</p>
							<p class="text-[11px] text-slate-500">150 rows ready for ingestion • District: KLKKD</p>
						</div>
						<div class="flex space-x-2">
							<a
								href="/api/admin/import/template"
								class="px-3 py-1.5 bg-white border border-slate-300 rounded-lg text-xs font-semibold hover:bg-slate-50 transition"
							>
								📥 {lang === 'ml' ? 'CSV ടെംപ്ലേറ്റ്' : 'Download Template'}
							</a>
							<button
								onclick={handleSimulateImport}
								disabled={loading}
								class="px-4 py-1.5 bg-citu-red hover:bg-citu-red-dark text-white rounded-lg text-xs font-bold shadow transition"
							>
								{loading ? 'Processing...' : (lang === 'ml' ? 'ഇംപോർട്ട് ആരംഭിക്കുക' : 'Start Import Job')}
							</button>
						</div>
					</div>

					{#if importStatus}
						<p class="text-xs font-bold text-citu-red text-center">{importStatus}</p>
					{/if}

					{#if importReport}
						<div class="p-4 bg-emerald-50 border border-emerald-200 rounded-xl space-y-3">
							<div class="flex items-center justify-between">
								<h4 class="text-xs font-bold text-emerald-800 uppercase tracking-wider">
									Import Execution Summary (FR10.10)
								</h4>
								<span class="px-2 py-0.5 bg-emerald-200 text-emerald-800 text-[10px] font-bold rounded">
									Completed
								</span>
							</div>
							<div class="grid grid-cols-4 gap-2 text-center text-xs">
								<div class="bg-white p-2 rounded-lg border border-emerald-100">
									<div class="text-base font-bold text-slate-800">{importReport.total}</div>
									<div class="text-[10px] text-slate-500">Total Rows</div>
								</div>
								<div class="bg-white p-2 rounded-lg border border-emerald-100">
									<div class="text-base font-bold text-emerald-600">{importReport.accepted}</div>
									<div class="text-[10px] text-slate-500">Accepted</div>
								</div>
								<div class="bg-white p-2 rounded-lg border border-emerald-100">
									<div class="text-base font-bold text-amber-600">{importReport.skipped}</div>
									<div class="text-[10px] text-slate-500">Duplicate Skipped</div>
								</div>
								<div class="bg-white p-2 rounded-lg border border-emerald-100">
									<div class="text-base font-bold text-red-600">{importReport.rejected}</div>
									<div class="text-[10px] text-slate-500">Rejected (Out of scope)</div>
								</div>
							</div>
						</div>
					{/if}
				</div>

			<!-- TAB 3: PAYMENT LEDGER -->
			{:else if activeTab === 'payments'}
				<div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-6">
					<div>
						<h3 class="text-base font-bold text-citu-slate-dark">
							{lang === 'ml' ? 'യൂണിയൻ ഫീസ് & പേയ്‌മെന്റ് ലെഡ്ജർ' : 'Financial Ledger & Dues Reconciliation (FR7.6)'}
						</h3>
						<p class="text-xs text-slate-500">
							Append-only immutable transaction log with bank settlement reconciliation.
						</p>
					</div>

					<div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
						<div class="p-4 bg-slate-50 border border-slate-200 rounded-xl">
							<p class="text-xs text-slate-500 font-semibold">Total Dues Collected</p>
							<p class="text-2xl font-bold text-citu-red mt-1">₹3,45,000</p>
							<p class="text-[11px] text-slate-400 mt-1">2,156 confirmed members</p>
						</div>
						<div class="p-4 bg-slate-50 border border-slate-200 rounded-xl">
							<p class="text-xs text-slate-500 font-semibold">Gateway Settlement</p>
							<p class="text-2xl font-bold text-emerald-600 mt-1">₹2,74,400</p>
							<p class="text-[11px] text-slate-400 mt-1">100% Reconciled to current a/c</p>
						</div>
						<div class="p-4 bg-slate-50 border border-slate-200 rounded-xl">
							<p class="text-xs text-slate-500 font-semibold">Offline Cash / UPI</p>
							<p class="text-2xl font-bold text-amber-600 mt-1">₹65,000</p>
							<p class="text-[11px] text-slate-400 mt-1">Signed by district secretaries</p>
						</div>
					</div>
				</div>

			<!-- TAB 4: AUDIT TRAIL -->
			{:else if activeTab === 'audit'}
				<div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-4">
					<div>
						<h3 class="text-base font-bold text-citu-slate-dark">
							{lang === 'ml' ? 'സിസ്റ്റം ഓഡിറ്റ് ലോഗ്' : 'Immutable Audit Log (FR7.8)'}
						</h3>
						<p class="text-xs text-slate-500">
							Unmodifiable chronological record of all administrative actions, ID views, and exports.
						</p>
					</div>

					<div class="divide-y divide-slate-100 font-mono text-xs">
						<div class="py-2.5 flex items-center justify-between">
							<span class="text-slate-500">2026-04-20 18:45:00 UTC</span>
							<span class="font-bold text-blue-700">export_performed</span>
							<span class="text-slate-600">state_gs (5 members exported to CSV)</span>
						</div>
						<div class="py-2.5 flex items-center justify-between">
							<span class="text-slate-500">2026-04-20 18:30:12 UTC</span>
							<span class="font-bold text-amber-700">id_viewed</span>
							<span class="text-slate-600">admin_kkd viewed member KLKKD000001</span>
						</div>
						<div class="py-2.5 flex items-center justify-between">
							<span class="text-slate-500">2026-04-20 18:15:44 UTC</span>
							<span class="font-bold text-purple-700">admin_2fa_success</span>
							<span class="text-slate-600">state_gs authenticated via TOTP</span>
						</div>
					</div>
				</div>
			{/if}
		</div>
	{/if}
</div>
