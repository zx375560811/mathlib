#ifndef DB_H
#define DB_H

void init_db();
void close_db();
void add_book(const char* title, const char* path);
void list_books();
void strip_newline(char* str);
void auto_import_books();
void delete_book(int id);
void update_book_title(int id, const char* new_title);
void search_books(const char* keyword);

#endif
