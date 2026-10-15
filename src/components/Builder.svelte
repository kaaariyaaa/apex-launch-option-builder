<script lang="ts">
  import { onMount } from 'svelte';

  import { type Option, type Ranking, inputType, parseRankings, renderOption, valid } from '../lib/options';
  type Selected = { id: string; value: string };
  const storageKey = 'apex-launch-option-builder:v1';
  const commandLimit = 259;
  export let base = '/';
  let options: Option[] = [];
  let rankings: Ranking[] = [];
  let query = '';
  let sort = 'recommended';
  let showExcluded = false;
  let loadError = '';
  let selected: Selected[] = [];
  let loading = true;
  let copied = false;
  let copyError = '';
  let ga: Window['gtag'] | undefined;

  $: visibleOptions = options.filter((option) => (showExcluded || option.candidate) && `${option.name} ${option.category} ${option.description} ${option.confidence} ${option.reasons.join(' ')} ${option.notes.join(' ')}`.toLowerCase().includes(query.trim().toLowerCase()));
  $: rankingById = new Map<string, number>(rankings.map((ranking) => [ranking.id, ranking.users]));
  $: matches = [...visibleOptions].sort((a, b) => {
    if (sort === 'popular') return (rankingById.get(b.id) ?? 0) - (rankingById.get(a.id) ?? 0) || a.name.localeCompare(b.name);
    if (sort === 'az') return a.name.localeCompare(b.name);
    if (sort === 'za') return b.name.localeCompare(a.name);
    return a.recommendation - b.recommendation || a.name.localeCompare(b.name);
  });
  $: selectedOptions = selected.map((item) => ({ item, option: options.find((option) => option.id === item.id) })).filter((entry): entry is { item: Selected; option: Option } => Boolean(entry.option));
  $: incomplete = selectedOptions.filter(({ item, option }) => !valid(item.value, option));
  $: command = selectedOptions.filter(({ item, option }) => valid(item.value, option)).map(({ item, option }) => renderOption(option, item.value)).join(' ');
  $: cfgOptions = selectedOptions.filter(({ item, option }) => option.cfg && valid(item.value, option)).map(({ item, option }) => option.format.replace(/^\+/, '').replace('{value}', item.value.trim()));

  onMount(async () => {
    try {
      const [optionsResponse, rankingResponse] = await Promise.all([
        fetch(`${base}data/registrations.json`), fetch(`${base}data/option-rankings.json`)
      ]);
      if (!optionsResponse.ok) throw new Error('オプションデータを読み込めませんでした');
      options = await optionsResponse.json();
      if (rankingResponse.ok) {
        try { rankings = parseRankings(await rankingResponse.text()); }
        catch { rankings = []; }
      }
      try {
        const saved = JSON.parse(localStorage.getItem(storageKey) ?? '[]');
        if (Array.isArray(saved)) selected = saved.filter((item) => item && typeof item.id === 'string' && options.some((option) => option.id === item.id)).map((item) => ({ id: item.id, value: String(item.value ?? '') }));
      } catch { localStorage.removeItem(storageKey); }
    } catch (error) {
      loadError = 'オプションデータを読み込めませんでした。再読み込みしてください。';
      console.error(error);
    } finally {
      loading = false;
    }
    const measurementId = import.meta.env.PUBLIC_GA_MEASUREMENT_ID;
    if (measurementId) {
      window.dataLayer = window.dataLayer || [];
      window.gtag = function(){ window.dataLayer.push(arguments); };
      window.gtag('js', new Date());
      window.gtag('config', measurementId, { anonymize_ip: true });
      const script = document.createElement('script');
      script.async = true;
      script.src = `https://www.googletagmanager.com/gtag/js?id=${measurementId}`;
      document.head.append(script);
      ga = window.gtag;
    }
  });

  $: if (!loading && typeof localStorage !== 'undefined') localStorage.setItem(storageKey, JSON.stringify(selected));

  function toggleOption(option: Option) {
    selected = selected.some((item) => item.id === option.id)
      ? selected.filter((item) => item.id !== option.id)
      : [...selected, { id: option.id, value: option.default ?? '' }];
  }
  function update(index: number, value: string) { selected = selected.map((item, i) => i === index ? { ...item, value } : item); }
  function reportSearch() {
    if (query.trim()) ga?.('event', 'view_search_results', { search_term: query.trim(), result_count: visibleOptions.length });
  }
  async function copyCommand() {
    copyError = '';
    try {
      await navigator.clipboard.writeText(command);
      for (const { option } of selectedOptions.filter(({ item, option }) => valid(item.value, option))) ga?.('event', 'option_copy', { option_id: option.id });
      copied = true;
      setTimeout(() => copied = false, 1800);
    } catch { copyError = 'コピーできませんでした。ブラウザの権限を確認してください。'; }
  }
</script>

<div class="app-shell">
  <header class="site-header"><a class="wordmark" href={base}>Apex Launch Option Builder</a></header>
  <main>
    <section class="builder-grid" aria-label="起動オプションビルダー">
      <section class="panel catalog" aria-label="起動オプション">
        <label class="searchbox"><span class="sr-only">オプションを検索</span><input bind:value={query} on:input={reportSearch} placeholder="名前・説明を検索" /></label>
        <div class="catalog-controls"><label class="sort-label">並び順<select bind:value={sort}><option value="recommended">候補優先</option><option value="popular">人気順</option><option value="az">名前 A–Z</option><option value="za">名前 Z–A</option></select></label><div class="filters"><label class="toggle-label"><input type="checkbox" bind:checked={showExcluded} />対象外も表示</label></div></div>
        <div class="table-head"><span>項目</span><span>既定値</span></div>
        <div class="option-list" aria-live="polite">
          {#if loadError}<div class="blank-state" role="alert">{loadError}</div>
          {:else if loading}<div class="blank-state">オプションを読み込んでいます…</div>
          {:else if !visibleOptions.length}<div class="blank-state">{options.length ? '一致する項目がありません。別のキーワードを試してください。' : 'オプションデータがありません。'}</div>
          {:else}
            {#each matches as option (option.id)}
              {@const isSelected = selected.some((item) => item.id === option.id)}
              <button class="option-item" class:selected={isSelected} on:click={(event) => event.detail === 0 && toggleOption(option)} on:dblclick={() => toggleOption(option)} aria-label={`${option.name}、ダブルクリックで${isSelected ? '解除' : '有効化'}` }>
                <span class="option-text"><span class="option-name">{option.name}{#if !option.candidate}<span class="badge">候補対象外</span>{/if}{#if isSelected}<span class="badge">選択中</span>{/if}</span><small>{option.description || option.category || '説明なし'}</small></span><code>{option.defaults.length > 1 ? '複数' : option.default || '—'}</code>
              </button>
            {/each}
          {/if}
        </div>
        <p class="data-note">実機での動作は未検証です。</p>

      </section>

      <section class="panel output" aria-labelledby="output-title">
        <div class="panel-title"><h2 id="output-title">選択した項目 <small>{selectedOptions.length}件</small></h2><button class="text-button" on:click={() => selected = []} disabled={!selected.length}>すべて削除</button></div>
        <div class="selection-area">
        {#if selectedOptions.length}
          <div class="selected-list">
            {#each selectedOptions as { item, option }, index (item.id)}
              <article class="selected-item"><div class="selected-item-head"><code>{option.name}</code><button class="remove" aria-label={`${option.name}を削除`} on:click={() => selected = selected.filter((entry) => entry.id !== item.id)}>削除</button></div>
                {#if option.value_kind !== '値なし'}
                  {#if !option.value_kind.startsWith('文字列') && option.value_kind.includes('0/1')}
                    <label class="value-field"><span>ON / OFF</span><select value={item.value} on:change={(event) => update(index, event.currentTarget.value)}><option value="" disabled>値を選択</option><option value="1">ON</option><option value="0">OFF</option></select></label>
                  {:else}{@const fieldType = inputType(option)}<label class="value-field"><span>{option.uncertain ? '引数部分（不要なら空欄）' : option.value_kind}{option.min_bound ? ` · ${option.min_bound}〜${option.max_bound || '上限なし'}` : ''}</span><input class:invalid={!valid(item.value, option)} type={fieldType} step={option.value_kind.includes('整数') && fieldType === 'number' ? '1' : 'any'} min={option.min_bound || undefined} max={option.max_bound || undefined} placeholder="値を入力" value={item.value} on:input={(event) => update(index, event.currentTarget.value)} /></label>{/if}
                  {#if !valid(item.value, option)}<small class="field-error">{item.value.trim() ? '入力形式を確認してください（改行・引用符・セミコロンは使用できません）。' : '値を入力してください。'}</small>{/if}
                {:else}<p class="no-value">この項目に値はありません</p>{/if}
              </article>
            {/each}
          </div>
        {:else}<div class="build-empty">選択した項目はありません。</div>{/if}
        </div>
        <div class="command-heading"><span>生成された起動コマンド</span><span>{command.length} / {commandLimit}文字</span></div>
        <div class="command-box" class:long={command.length >= commandLimit}><code>{command || 'ここにコマンドが表示されます'}</code></div>
        {#if incomplete.length}<p class="notice error-notice">値が未入力または範囲外の項目があります。入力するとコマンドに含まれます。</p>{/if}
        <button class="copy-button" disabled={!command || incomplete.length > 0} on:click={copyCommand}>{copied ? 'コピーしました' : 'コマンドをコピー'}</button>
        {#if copyError}<p class="notice error-notice">{copyError}</p>{/if}
        {#if command.length >= commandLimit}<section class="cfg-card"><span class="cfg-icon">↳</span><div><strong>CFGファイルの利用を検討できます</strong><p>259文字以上になりました。CFGに移せる設定だけを分けて表示しています。起動オプション自体はこのままコピーできます。</p>{#if cfgOptions.length}<span class="cfg-label">CFGに記述できる設定</span><code class="cfg-code">{cfgOptions.join('\n')}</code>{:else}<p>選択中の項目にCFG移行可能と確認された設定はありません。</p>{/if}<p class="cfg-help">テキストエディターで設定を1行ずつ記述し、Apex Legendsの <code>cfg</code> フォルダーへ <code>autoexec.cfg</code> として保存します。ゲーム起動オプションに <code>+exec autoexec</code> を追加して読み込みます。対応状況はゲーム更新で変わる場合があります。</p></div></section>{/if}
      </section>
    </section>
    <footer>ゲームのアップデートにより、登録項目が使えなくなる場合があります。</footer>
  </main>
</div>
