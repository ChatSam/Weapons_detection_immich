<script lang="ts">
  import { type WeaponsDetectItem} from '@api';

  export let weapon: WeaponsDetectItem;
</script>

<div class="flex gap-4 px-6 py-2">
  <div class="h-full w-full shrink-0 bg-slate-300">
    {#if weapon.image}
      <img
        src={weapon.image}
        alt={"Weapon image"}
        class="z-0 h-full w-full object-contain"
        data-testid="weapon-image"
        draggable="false"
      />
    {/if}
  </div>
  <!-- <div class="flex h-12 flex-col items-start justify-center overflow-hidden">
    <span class="w-full shrink overflow-hidden text-ellipsis whitespace-nowrap">
      <b>{weapon.score}</b>
    </span> -->
  <!-- </div> -->
</div>
