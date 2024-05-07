<script lang="ts">
    import {api } from '@api';
    import { createEventDispatcher, onMount } from 'svelte';
    import BaseModal from './base-modal.svelte';
    import WeaponsListItem from '../asset-viewer/weapons-list-item.svelte';
    import { handleError } from '$lib/utils/handle-error';
  
    let weaponFilePath: string = '';
    let mediaMode: string = '';
    let loading = true;
    export let assetId: string = '';
  
    const dispatch = createEventDispatcher<{
      close: void;
    }>();
  
    onMount(async () => {
      
      try {
        const { data } = await api.weaponsDetectApi.getWeaponsDetect({ id: assetId });
        weaponFilePath = data.filePath;
        mediaMode = data.mediaMode;
      } catch (error) {
      handleError(error, "Internal Server Error! Cannot Detect Weapons.");
    }

      loading = false;
    });
  
  </script>
  
  <BaseModal on:close={() => dispatch('close')}>
    <svelte:fragment slot="title">
      <span class="flex place-items-center gap-2">
        <p class="font-medium">
          {#if loading}
            Detecting...
          {:else if weaponFilePath !== ''}
            Weapon Detected!
          {:else}
            No Weapon Detected!
          {/if}
        </p>
      </span>
    </svelte:fragment>
  
    <div class="mb-2 flex max-h-[90vh] flex-col">
      {#if loading}
        {#each { length: 3 } as _}
          <div class="flex animate-pulse gap-4 px-6 py-2">
            <div class="h-12 w-12 rounded-xl bg-slate-200" />
            <div class="flex flex-col items-start justify-center gap-2">
              <span class="h-4 w-36 animate-pulse bg-slate-200" />
              <div class="flex animate-pulse gap-1">
                <span class="h-3 w-8 bg-slate-200" />
                <span class="h-3 w-20 bg-slate-200" />
              </div>
            </div>
          </div>
        {/each}
      {:else}
        <!-- svelte-ignore a11y-autofocus -->
        <div class="immich-scrollbar overflow-y-auto">
          {#if weaponFilePath !== ''}
            <div class="flex gap-4 px-6 py-2">
              <div class="h-full w-full shrink-0 bg-slate-300">
                <WeaponsListItem assetId={assetId} weaponFilePath={weaponFilePath} mediaMode={mediaMode} />
              </div>
            </div>
          {:else}
            <div class="flex gap-4 px-6 py-2">
              <div class="h-300 w-300 shrink-0 bg-slate-300">
                <WeaponsListItem assetId={assetId} weaponFilePath={'/ElmerFuddBg.png'} mediaMode={'image'} />
              </div>
            </div>
          {/if}
        </div>
      {/if}
    </div>
  </BaseModal>
  