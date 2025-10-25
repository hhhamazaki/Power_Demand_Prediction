/**
 * アプリケーション定数定義
 * 開発ガイドライン準拠: 定数は大文字スネークケースで命名
 */
/**
 * アプリケーション定数定義
 * 開発ガイドライン準拠: 定数は大文字スネークケースで命名
 */

export const EXPENSE_CATEGORIES = {
    TRANSPORTATION: '交通費',
    MEAL: '飲食費',
    SUPPLY: '消耗品費',
    COMMUNICATION: '通信費',
    ENTERTAINMENT: '接待費',
    OTHER: 'その他'
};

export const VALIDATION_RULES = {
    TITLE: {
        MIN_LENGTH: 1,
        MAX_LENGTH: 50
    },
    AMOUNT: {
        MIN_VALUE: 1,
        MAX_VALUE: 1000000
    },
    REMARK: {
        MAX_LENGTH: 200
    }
};

export const LOCAL_STORAGE_KEYS = {
    EXPENSE_DATA: 'expenseData',
    LAST_CODE_NUMBER: 'lastCodeNumber',
    SETTINGS: 'expenseSettings',
    COMPLETION_CODES: 'completionCodes'
};

export const STATUS_TYPES = {
    PENDING: '未処理',
    PROCESSED: '処理済み'
};

export const ERROR_MESSAGES = {
    VALIDATION: {
        TITLE_REQUIRED: 'タイトルは必須です',
        TITLE_TOO_LONG: 'タイトルは50文字以下で入力してください',
        AMOUNT_INVALID: '金額は1円以上1,000,000円以下で入力してください',
        CATEGORY_REQUIRED: '種別を選択してください'
    },
    STORAGE: {
        SAVE_FAILED: 'データの保存に失敗しました',
        LOAD_FAILED: 'データの読み込みに失敗しました'
    },
    FILE: {
        INVALID_FORMAT: '対応していないファイル形式です',
        SIZE_TOO_LARGE: 'ファイルサイズが大きすぎます'
    }
};

export const PERFORMANCE_CONFIG = {
    DEBOUNCE_DELAY: 300,
    THROTTLE_LIMIT: 100,
    VIRTUAL_SCROLL_ITEM_HEIGHT: 50,
    CHART_ANIMATION_DURATION: 1000
};


export const SECURITY_CONFIG = {
    MAX_REQUESTS_PER_MINUTE: 60,
    SESSION_TIMEOUT_MINUTES: 30,
    MAX_FILE_SIZE_MB: 5
};

export const CONSTANTS = {
    EXPENSE_CATEGORIES,
    VALIDATION_RULES,
    LOCAL_STORAGE_KEYS,
    STATUS_TYPES,
    ERROR_MESSAGES,
    PERFORMANCE_CONFIG,
    SECURITY_CONFIG
};
