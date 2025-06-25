#include <sqlite3.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <sys/types.h>
#include <ctype.h>

sqlite3* db;

void init_db() {
    if (sqlite3_open("books.db", &db)) {
        fprintf(stderr, "无法打开数据库: %s\n", sqlite3_errmsg(db));
        exit(1);
    }
    const char* sql = "CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY, title TEXT, path TEXT);";
    sqlite3_exec(db, sql, 0, 0, 0);
}

void close_db() {
    sqlite3_close(db);
}

void add_book(const char* title, const char* path) {
    sqlite3_stmt* stmt;
    sqlite3_prepare_v2(db, "INSERT INTO books (title, path) VALUES (?, ?);", -1, &stmt, 0);
    sqlite3_bind_text(stmt, 1, title, -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 2, path, -1, SQLITE_STATIC);
    sqlite3_step(stmt);
    sqlite3_finalize(stmt);
}

void list_books() {
    sqlite3_stmt* stmt;
    sqlite3_prepare_v2(db, "SELECT id, title FROM books;", -1, &stmt, 0);
    printf("📚 当前书籍列表：\n");
    while (sqlite3_step(stmt) == SQLITE_ROW) {
        printf("%d. %s\n", sqlite3_column_int(stmt, 0), sqlite3_column_text(stmt, 1));
    }
    sqlite3_finalize(stmt);
}

void strip_newline(char* str) {
    char* p = strchr(str, '\n');
    if (p) *p = '\0';
}

void auto_import_books() {
    const char* folder = "ebooks";
    struct dirent* entry;
    DIR* dir = opendir(folder);

    if (!dir) {
        printf("⚠️ 无法打开 ebooks 文件夹。\n");
        return;
    }

    int count = 0;
    while ((entry = readdir(dir)) != NULL) {
        const char* filename = entry->d_name;
        size_t len = strlen(filename);

        if (len > 4 && strcasecmp(filename + len - 4, ".pdf") == 0) {
            char path[512];
            snprintf(path, sizeof(path), "%s/%s", folder, filename);

            char title[256];
            strncpy(title, filename, len - 4);
            title[len - 4] = '\0';

            add_book(title, path);
            count++;
        }
    }

    closedir(dir);
    printf("✅ 成功导入 %d 本书。\n", count);
}

void delete_book(int id) {
    sqlite3_stmt* stmt;
    sqlite3_prepare_v2(db, "DELETE FROM books WHERE id=?;", -1, &stmt, 0);
    sqlite3_bind_int(stmt, 1, id);
    if (sqlite3_step(stmt) == SQLITE_DONE) {
        printf("✅ 已删除书籍 ID=%d。\n", id);
    } else {
        printf("❌ 删除失败。\n");
    }
    sqlite3_finalize(stmt);
}

void update_book_title(int id, const char* new_title) {
    sqlite3_stmt* stmt;
    sqlite3_prepare_v2(db, "UPDATE books SET title=? WHERE id=?;", -1, &stmt, 0);
    sqlite3_bind_text(stmt, 1, new_title, -1, SQLITE_STATIC);
    sqlite3_bind_int(stmt, 2, id);
    if (sqlite3_step(stmt) == SQLITE_DONE) {
        printf("✅ 已更新书名。\n");
    } else {
        printf("❌ 修改失败。\n");
    }
    sqlite3_finalize(stmt);
}

void search_books(const char* keyword) {
    sqlite3_stmt* stmt;
    char query[300];
    snprintf(query, sizeof(query), "SELECT id, title FROM books WHERE title LIKE ?;");
    sqlite3_prepare_v2(db, query, -1, &stmt, 0);

    char pattern[256];
    snprintf(pattern, sizeof(pattern), "%%%s%%", keyword);  // "%keyword%"
    sqlite3_bind_text(stmt, 1, pattern, -1, SQLITE_STATIC);

    printf("🔍 搜索结果：\n");
    int found = 0;
    while (sqlite3_step(stmt) == SQLITE_ROW) {
        printf("%d. %s\n", sqlite3_column_int(stmt, 0), sqlite3_column_text(stmt, 1));
        found = 1;
    }
    if (!found) {
        printf("❌ 没有找到匹配的书籍。\n");
    }
    sqlite3_finalize(stmt);
}
