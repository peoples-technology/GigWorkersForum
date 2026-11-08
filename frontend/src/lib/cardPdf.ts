/**
 * Generates an ISO/IEC 7810 CR80 compliant PDF document (85.60mm x 53.98mm)
 * directly from an HTML5 canvas element or image data URL in pure client-side TypeScript.
 * Zero external heavy dependencies, works 100% offline and cross-browser.
 */
export function generateCardPdfFromDataUrl(
	imgDataUrl: string,
	canvasWidth = 1012,
	canvasHeight = 638
): Blob {
	// Fallback 1x1 valid JPEG if empty or running in canvas-less environments
	const validDataUrl =
		imgDataUrl && imgDataUrl.includes(',')
			? imgDataUrl
			: 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////wgALCAABAAEBAREA/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxA=';

	const base64 = validDataUrl.split(',')[1] || '';
	const binary = atob(base64);
	const imgLen = binary.length;

	// CR80 dimensions in PostScript points (72 points = 1 inch)
	// 85.60 mm * (72 / 25.4) = 242.64 pt
	// 53.98 mm * (72 / 25.4) = 153.00 pt
	const widthPt = 242.64;
	const heightPt = 153.00;

	// PDF Objects
	const header = '%PDF-1.4\n%\xE2\xE3\xCF\xD3\n';
	const obj1 = '1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n';
	const obj2 = '2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n';
	const obj3 = `3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ${widthPt.toFixed(2)} ${heightPt.toFixed(2)}] /Resources << /XObject << /Im0 4 0 R >> >> /Contents 5 0 R >>\nendobj\n`;

	const imgHeader = `4 0 obj\n<< /Type /XObject /Subtype /Image /Width ${canvasWidth} /Height ${canvasHeight} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length ${imgLen} >>\nstream\n`;
	const imgFooter = '\nendstream\nendobj\n';

	const contentStream = `q\n${widthPt.toFixed(2)} 0 0 ${heightPt.toFixed(2)} 0 0 cm\n/Im0 Do\nQ\n`;
	const obj5 = `5 0 obj\n<< /Length ${contentStream.length} >>\nstream\n${contentStream}endstream\nendobj\n`;

	// Compute byte offsets for cross-reference table (xref)
	let offset = header.length;
	const o1 = offset;
	offset += obj1.length;
	const o2 = offset;
	offset += obj2.length;
	const o3 = offset;
	offset += obj3.length;
	const o4 = offset;
	offset += imgHeader.length + imgLen + imgFooter.length;
	const o5 = offset;
	offset += obj5.length;

	const xref = `xref\n0 6\n0000000000 65535 f \n${String(o1).padStart(10, '0')} 00000 n \n${String(o2).padStart(10, '0')} 00000 n \n${String(o3).padStart(10, '0')} 00000 n \n${String(o4).padStart(10, '0')} 00000 n \n${String(o5).padStart(10, '0')} 00000 n \n`;
	const trailer = `trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n${offset}\n%%EOF\n`;

	// Assemble binary parts
	const encoder = new TextEncoder();
	const bytesBeforeImg = encoder.encode(header + obj1 + obj2 + obj3 + imgHeader);
	const imgBytes = new Uint8Array(imgLen);
	for (let i = 0; i < imgLen; i++) {
		imgBytes[i] = binary.charCodeAt(i);
	}
	const bytesAfterImg = encoder.encode(imgFooter + obj5 + xref + trailer);

	return new Blob([bytesBeforeImg, imgBytes, bytesAfterImg], { type: 'application/pdf' });
}

export function generateCardPdfBlob(canvas: HTMLCanvasElement): Blob {
	let imgDataUrl = '';
	try {
		imgDataUrl = canvas.toDataURL('image/jpeg', 0.95);
	} catch (e) {
		console.warn('Canvas toDataURL failed or mocked:', e);
	}
	return generateCardPdfFromDataUrl(imgDataUrl, canvas.width || 1012, canvas.height || 638);
}

export function downloadCardPdf(canvas: HTMLCanvasElement, filename: string) {
	const blob = generateCardPdfBlob(canvas);
	const url = URL.createObjectURL(blob);
	const a = document.createElement('a');
	a.href = url;
	a.download = filename.endsWith('.pdf') ? filename : `${filename}.pdf`;
	document.body.appendChild(a);
	a.click();
	setTimeout(() => {
		document.body.removeChild(a);
		URL.revokeObjectURL(url);
	}, 200);
}
