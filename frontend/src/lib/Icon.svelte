<script lang="ts">
	import { MATERIAL_ICONS } from '$lib/icons';

	let {
		name = '',
		class: className = '',
		size = '1em'
	}: {
		name: string;
		class?: string;
		size?: string | number;
	} = $props();

	let pathD = $derived(MATERIAL_ICONS[name] || '');
	let formattedSize = $derived(typeof size === 'number' ? `${size}px` : size);
</script>

{#if pathD}
	<svg
		xmlns="http://www.w3.org/2000/svg"
		viewBox="0 -960 960 960"
		width={formattedSize}
		height={formattedSize}
		fill="currentColor"
		class="inline-block shrink-0 align-middle {className}"
		aria-hidden="true"
	>
		<path d={pathD} />
	</svg>
{:else}
	<span class="inline-block shrink-0 align-middle {className}" aria-hidden="true"></span>
{/if}
