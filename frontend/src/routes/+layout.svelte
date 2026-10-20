<script lang="ts">
	import '../app.css';
	let { children } = $props();
</script>

<div class="min-h-screen flex flex-col bg-surface text-on-surface antialiased">
	{@render children?.()}
</div>
