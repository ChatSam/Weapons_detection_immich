<script lang="ts">
  import WeaponPhotoViewer from './weapon-photo-viewer.svelte';
  import WeaponVideoViewer from './weapon-video-viewer.svelte';

  export let weaponFilePath: string = '';
  export let mediaMode: string = '';
  export let assetId: string = '';

  const handleVideoStarted = () => {
  };

  const handleVideoEnded = async () => {
  };

</script>

<div class="flex gap-4">
  <div class="h-full w-full shrink-0 bg-slate-300">
    {#if mediaMode === 'image'}
      <WeaponPhotoViewer filePath={weaponFilePath} />
    {:else}
      <WeaponVideoViewer assetId={assetId} filePath={weaponFilePath} on:onVideoEnded={handleVideoEnded} on:onVideoStarted={handleVideoStarted}/>
  {/if}
  </div>
</div>
