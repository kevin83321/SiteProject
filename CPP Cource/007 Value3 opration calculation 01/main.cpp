#include <iostream>
using namespace std; 
/* run this program using the console pauser or add your own getch, system("pause") or input loop */

int main(int argc, char** argv) {
	cout<< "請輸入一個整數 =>";
	int a;
	cin>>a;

	cout<< "請輸入一個整數 =>";
	int b;
	cin>>b;
	
	int c = a + b;
	int d = a - b;
	int e = a * b;
	int f = a / b;
	int g = a % b;
	
	cout << a << "+" << b << "=" << c << endl;
	cout << a << "-" << b << "=" << d << endl;
	cout << a << "*" << b << "=" << e << endl;
	cout << a << "/" << b << "=" << f << endl;
	cout << a << "%" << b << "=" << g << endl;
	if (g==0){
		cout << a << "是" << b << "的倍數" << endl;
	} else{
		cout << a << "不是" << b << "的倍數" << endl;
	}
	return 0;
}
