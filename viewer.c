#include <sqlite3.h>
#include <stdio.h>
#include "db.h"

extern sqlite3* db;

void open_book(int id) {
    sqlite3_stmt* stmt;
    sqlite3_prepare_v2(db, "SELECT path FROM books WHERE id=?;", -1, &stmt, 0);
    sqlite3_bind_int(stmt, 1, id);

    if (sqlite3_step(stmt) == SQLITE_ROW) {
        const char* path = (const char*)sqlite3_column_text(stmt, 0);
        printf("📂 如果在本地，这里将打开文件：%s\n", path);

        // 以下命令只适用于本地带 GUI 的环境（如 Ubuntu Desktop）
        // char cmd[600];
        // snprintf(cmd, sizeof(cmd), "xdg-open \"%s\"", path);
        // system(cmd);
    } else {
        printf("❌ 未找到对应书籍。\n");
    }

    sqlite3_finalize(stmt);
}
