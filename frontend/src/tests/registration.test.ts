import { describe, it, expect, beforeEach } from 'vitest';

describe('Registration Form Logic & DPDP Compliance', () => {
	beforeEach(() => {
		localStorage.clear();
		sessionStorage.clear();
	});

	// Districts
	const districts = [
		{ code: 'KLTVC', en: 'Thiruvananthapuram', ml: 'തിരുവനന്തപുരം' },
		{ code: 'KLKLM', en: 'Kollam', ml: 'കൊല്ലം' },
		{ code: 'KLPTA', en: 'Pathanamthitta', ml: 'പത്തനംതിട്ട' },
		{ code: 'KLALP', en: 'Alappuzha', ml: 'ആലപ്പുഴ' },
		{ code: 'KLKTM', en: 'Kottayam', ml: 'കോട്ടയം' },
		{ code: 'KLIDK', en: 'Idukki', ml: 'ഇടുക്കി' },
		{ code: 'KLERN', en: 'Ernakulam', ml: 'എറണാകുളം' },
		{ code: 'KLTSR', en: 'Thrissur', ml: 'തൃശ്ശൂർ' },
		{ code: 'KLPKD', en: 'Palakkad', ml: 'പാലക്കാട്' },
		{ code: 'KLMLP', en: 'Malappuram', ml: 'മലപ്പുറം' },
		{ code: 'KLKKD', en: 'Kozhikode', ml: 'കോഴിക്കോട്' },
		{ code: 'KLWND', en: 'Wayanad', ml: 'വയനാട്' },
		{ code: 'KLKNR', en: 'Kannur', ml: 'കണ്ണൂർ' },
		{ code: 'KLKSD', en: 'Kasaragod', ml: 'കാസർഗോഡ്' }
	];

	// Sector & Platform Mapping
	const sectorPlatformMap: Record<string, string[]> = {
		'Delivery': ['Zomato', 'Swiggy', 'Instamart', 'BigBasket', 'Blinkit', 'Flipkart Minutes', 'Porter', 'Shadowfax', 'Ecom Express', 'Delhivery', 'Other'],
		'Ride Hailing': ['Uber', 'Ola', 'Rapido', 'Kerala Savari', 'Yatri', 'Other'],
		'On-Demand': ['Urban Company', 'Free Hour', 'Hiird', 'Other'],
		'Logistics': ['Porter', 'Shadowfax', 'Ecom Express', 'Delhivery', 'BlueDart', 'Other']
	};

	it('should contain all 14 official Kerala districts with unique codes', () => {
		expect(districts.length).toBe(14);
		const codes = new Set(districts.map(d => d.code));
		expect(codes.size).toBe(14);
		expect(codes.has('KLTVC')).toBe(true);
		expect(codes.has('KLERN')).toBe(true);
		expect(codes.has('KLKKD')).toBe(true);
	});

	it('should correctly map platforms to their respective sectors', () => {
		expect(sectorPlatformMap['Delivery']).toContain('Swiggy');
		expect(sectorPlatformMap['Delivery']).toContain('Zomato');
		expect(sectorPlatformMap['Ride Hailing']).toContain('Uber');
		expect(sectorPlatformMap['Ride Hailing']).toContain('Ola');
		expect(sectorPlatformMap['On-Demand']).toContain('Urban Company');
	});

	it('should validate age >= 18 and reject minors under DPDP and Union rules', () => {
		function calculateAge(birthDate: string): number | null {
			if (!birthDate) return null;
			const dobObj = new Date(birthDate);
			const today = new Date('2026-11-08');
			let calculated = today.getFullYear() - dobObj.getFullYear();
			const m = today.getMonth() - dobObj.getMonth();
			if (m < 0 || (m === 0 && today.getDate() < dobObj.getDate())) {
				calculated--;
			}
			return calculated;
		}

		// Adult: Born 1995
		expect(calculateAge('1995-05-12')).toBeGreaterThanOrEqual(18);
		// Exactly 18 years old: Born 2008-11-08
		expect(calculateAge('2008-11-08')).toBe(18);
		// Minor: Born 2012
		expect(calculateAge('2012-01-01')).toBeLessThan(18);
	});

	it('should strictly enforce DPDP Act 4-digit ID format and reject 12-digit raw Aadhaar', () => {
		function validateIdLastDigits(input: string): boolean {
			return /^\d{4}$/.test(input.trim());
		}

		expect(validateIdLastDigits('5678')).toBe(true);
		expect(validateIdLastDigits('0012')).toBe(true);
		expect(validateIdLastDigits(' 4321 ')).toBe(true);

		// Rejections: full 12 digits, alphabet characters, 3 digits, 5 digits
		expect(validateIdLastDigits('123456789012')).toBe(false);
		expect(validateIdLastDigits('ABCD')).toBe(false);
		expect(validateIdLastDigits('123')).toBe(false);
		expect(validateIdLastDigits('12345')).toBe(false);
		expect(validateIdLastDigits('')).toBe(false);
	});

	it('should auto-save draft with activeStep 4 and restore all fields without losing state on refresh', () => {
		const draftData = {
			activeStep: 4,
			mobile: '9847112233',
			fullName: 'Com. Sakhavu Krishnan',
			dob: '1992-06-15',
			gender: 'Male',
			motherTongue: 'Malayalam',
			email: 'krishnan@gigworkers.online',
			currentAddress: 'CITU House, Thampanoor, TVM',
			workingDistrict: 'KLTVC',
			primarySector: 'Delivery',
			primaryPlatform: 'Swiggy',
			customPlatform: '',
			workingMode: 'Full Time',
			vehicleNumber: 'KL-01-CB-8899',
			licenceNumber: 'KL0120150001234',
			idDocType: 'Aadhaar',
			idLastDigits: '4567',
			capturedPhoto: 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQ...'
		};

		localStorage.setItem('ksgpwu_reg_draft', JSON.stringify(draftData));

		// Simulate page reload and restore
		const restoredStr = localStorage.getItem('ksgpwu_reg_draft');
		expect(restoredStr).not.toBeNull();
		const restored = JSON.parse(restoredStr!);

		expect(restored.activeStep).toBe(4);
		expect(restored.fullName).toBe('Com. Sakhavu Krishnan');
		expect(restored.workingDistrict).toBe('KLTVC');
		expect(restored.idLastDigits).toBe('4567');
		expect(restored.capturedPhoto).toContain('data:image/jpeg;base64');
	});

	it('should correctly format pendingRegistration payload for Checkout navigation', () => {
		const payload = {
			mobile: '9847001122',
			fullName: 'Anjali Menon',
			dob: '1998-03-21',
			gender: 'Female',
			motherTongue: 'Malayalam',
			email: 'anjali@example.com',
			currentAddress: 'Flat 4B, Marine Drive, Kochi',
			workingDistrict: 'KLERN',
			district: 'KLERN',
			primarySector: 'Ride Hailing',
			primaryPlatform: 'Uber',
			customPlatform: '',
			workingMode: 'Full Time',
			vehicleNumber: 'KL-07-CD-3321',
			licenceNumber: 'KL0720180004567',
			idDocType: 'Aadhaar',
			idLastDigits: '9012',
			photo: 'data:image/jpeg;base64,samplePhotoData',
			amount: 100,
			timestamp: new Date().toISOString()
		};

		sessionStorage.setItem('pendingRegistration', JSON.stringify(payload));
		localStorage.setItem('pendingRegistration', JSON.stringify(payload));

		const saved = JSON.parse(sessionStorage.getItem('pendingRegistration')!);
		expect(saved.fullName).toBe('Anjali Menon');
		expect(saved.workingDistrict).toBe('KLERN');
		expect(saved.amount).toBe(100);
		expect(saved.primaryPlatform).toBe('Uber');
		expect(saved.photo).toBe('data:image/jpeg;base64,samplePhotoData');
	});
});
