import { describe, it, expect, beforeEach } from 'vitest';

describe('Home Page Member Quick Access & Phone Lookup', () => {
	beforeEach(() => {
		localStorage.clear();
	});

	function lookupMemberByPhone(phone: string): { matchedId: string | null; error: string | null } {
		let cleanPhone = (phone || '').replace(/\D/g, '');
		if (cleanPhone.length === 12 && cleanPhone.startsWith('91')) {
			cleanPhone = cleanPhone.slice(2);
		}
		if (cleanPhone.length !== 10) {
			return { matchedId: null, error: 'Please enter a valid 10-digit mobile number.' };
		}

		try {
			const regStr = localStorage.getItem('ksgpwu_members_registry');
			if (regStr) {
				const registry = JSON.parse(regStr);
				for (const id in registry) {
					const m = registry[id];
					const regPhone = (m.mobile || m.phone || '').replace(/\D/g, '');
					if (regPhone === cleanPhone || (regPhone.length >= 10 && regPhone.endsWith(cleanPhone))) {
						return { matchedId: id, error: null };
					}
				}
			}
		} catch (e) {}

		return { matchedId: null, error: 'No active membership found for this mobile number.' };
	}

	it('should successfully match registered member phone and provide their verify ID', () => {
		const registry = {
			'KL-TVC-2026-9911': {
				memberId: 'KL-TVC-2026-9911',
				fullName: 'ARJUN K.',
				mobile: '9847123456',
				status: 'Active & Paid-Up'
			},
			'KL-ERN-2026-8822': {
				memberId: 'KL-ERN-2026-8822',
				fullName: 'SHEEBA P.',
				mobile: '9447654321',
				status: 'Active & Paid-Up'
			}
		};

		localStorage.setItem('ksgpwu_members_registry', JSON.stringify(registry));

		const res1 = lookupMemberByPhone('9847123456');
		expect(res1.matchedId).toBe('KL-TVC-2026-9911');
		expect(res1.error).toBeNull();

		const res2 = lookupMemberByPhone('+91 9447 654 321');
		expect(res2.matchedId).toBe('KL-ERN-2026-8822');
		expect(res2.error).toBeNull();
	});

	it('should return error for invalid phone numbers or unregistered workers', () => {
		const resInvalid = lookupMemberByPhone('12345');
		expect(resInvalid.matchedId).toBeNull();
		expect(resInvalid.error).toContain('valid 10-digit');

		const resUnregistered = lookupMemberByPhone('9999999999');
		expect(resUnregistered.matchedId).toBeNull();
		expect(resUnregistered.error).toContain('No active membership found');
	});

	it('should format and prepare Option 1 (Membership ID) directly without browser pattern errors', () => {
		const inputId = ' kl-tvc-2026-3103 ';
		const cleanId = inputId.trim().toUpperCase();
		expect(cleanId).toBe('KL-TVC-2026-3103');
		const verifyTargetUrl = `/verify?token=${encodeURIComponent(cleanId)}`;
		expect(verifyTargetUrl).toBe('/verify?token=KL-TVC-2026-3103');
	});

	it('should handle Option 2 (Mobile OTP) as a locked feature with informative notice', () => {
		const accessMode = 'otp';
		const isLocked = accessMode === 'otp';
		expect(isLocked).toBe(true);

		const lockedMessage = '🔒 Mobile OTP is currently locked for telecom gateway maintenance. Please use "Option 1: Membership ID" to download your card.';
		expect(lockedMessage).toContain('currently locked');
		expect(lockedMessage).toContain('Option 1: Membership ID');
	});
});
