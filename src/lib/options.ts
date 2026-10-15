export type Option = {
    id: string; name: string; default: string; value_kind: string; min_bound: string; max_bound: string;
    help: string; description: string; confidence: string; category: string; deprecated: boolean;
    internal: boolean; recommendation: number; cfg: boolean; format: string;
    candidate: boolean; defaults: string[]; example: string; uncertain: boolean;
    reasons: string[]; notes: string[]; sources: string[]; registrations: number;
  };

export function renderOption(option: Option, value: string) {
    const trimmed = value.trim();
    const argument = !option.uncertain && (!trimmed || /\s/.test(trimmed)) ? `"${trimmed}"` : trimmed;
    return option.format.replace('{value}', () => argument).trim();
  }
  export function valid(value: string, option: Option) {
    if (option.value_kind === '値なし') return true;
    if (/[\r\n";]/.test(value)) return false;
    if (option.uncertain) return true;
    if (!value.trim()) return option.value_kind.includes('空値可');
    if (option.value_kind.startsWith('文字列')) return true;
    if (option.value_kind.includes('0/1')) return value === '0' || value === '1';
    if (/整数|数値|浮動小数|小数/.test(option.value_kind)) {
      const number = Number(value);
      return Number.isFinite(number) && (!option.value_kind.includes('整数') || Number.isInteger(number));
    }
    return true;
  }
