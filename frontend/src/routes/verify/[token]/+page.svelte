<script lang="ts">
	import { page } from '$app/stores';
	import VerifyCardView from '$lib/VerifyCardView.svelte';
</script>

<VerifyCardView token={$page.params.token} />
