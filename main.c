#include <stdio.h>
#include "db.h"
#include "viewer.h"

int main() {
    init_db();

    int choice;
    while (1) {
        printf("\n========= Math eBook Manager =========\n");
        printf("[1] 添加书籍\n");
        printf("[2] 查看书籍\n");
        printf("[3] 打开书籍\n");
        printf("[4] 删除书籍\n");
        printf("[5] 修改书名\n");
        printf("[6] 搜索书籍\n");
        printf("[9] 扫描 ebooks 文件夹自动添加\n");
        printf("[0] 退出\n");
        printf("请选择操作：");
        scanf("%d", &choice);
        getchar(); // 清除回车

        if (choice == 1) {
            char title[256], path[512];
            printf("请输入书名：");
            fgets(title, sizeof(title), stdin);
            printf("请输入路径：");
            fgets(path, sizeof(path), stdin);
            strip_newline(title);
            strip_newline(path);
            add_book(title, path);
            printf("书籍已添加。\n");
        }

        else if (choice == 2) {
            list_books();
        }

        else if (choice == 3) {
            int id;
            printf("请输入书籍 ID：");
            scanf("%d", &id);
            getchar();
            open_book(id);
        }

        else if (choice == 4) {
            int id;
            printf("请输入要删除的书籍 ID：");
            scanf("%d", &id);
            getchar();
            delete_book(id);
        }

        else if (choice == 5) {
            int id;
            char new_title[256];
            printf("请输入要修改的书籍 ID：");
            scanf("%d", &id);
            getchar();
            printf("请输入新的书名：");
            fgets(new_title, sizeof(new_title), stdin);
            strip_newline(new_title);
            update_book_title(id, new_title);
        }

        else if (choice == 6) {
            char keyword[256];
            printf("请输入关键词：");
            fgets(keyword, sizeof(keyword), stdin);
            strip_newline(keyword);
            search_books(keyword);
        }

        else if (choice == 9) {
            auto_import_books();
        }

        else if (choice == 0) {
            break;
        }

        else {
            printf("无效选择，请重新输入。\n");
        }
    }

    close_db();
    return 0;
}
