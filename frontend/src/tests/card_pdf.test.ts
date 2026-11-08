import { describe, it, expect } from 'vitest';
import { generateCardPdfBlob } from '../lib/cardPdf';

describe('Card PDF Generation', () => {
	it('should generate a valid PDF blob conforming to ISO/IEC 7810 CR80 dimensions', async () => {
		// Mock canvas
		const canvas = document.createElement('canvas');
		canvas.width = 1012;
		canvas.height = 638;
		const ctx = canvas.getContext('2d');
		if (ctx) {
			ctx.fillStyle = '#C62828';
			ctx.fillRect(0, 0, 1012, 130);
			ctx.fillStyle = '#FFFFFF';
			ctx.fillRect(0, 130, 1012, 508);
		}

		const pdfBlob = generateCardPdfBlob(canvas);
		expect(pdfBlob.type).toBe('application/pdf');
		expect(pdfBlob.size).toBeGreaterThan(100);

		const arrayBuffer = await pdfBlob.arrayBuffer();
		const uint8Array = new Uint8Array(arrayBuffer);
		const text = new TextDecoder().decode(uint8Array);

		// Must start with PDF header
		expect(text.startsWith('%PDF-1.4')).toBe(true);

		// Must have CR80 MediaBox dimensions (242.64 pt x 153.00 pt)
		expect(text).toContain('242.64 153.00');

		// Must have xref table and EOF marker
		expect(text).toContain('xref');
		expect(text).toContain('%%EOF');
	});
});
