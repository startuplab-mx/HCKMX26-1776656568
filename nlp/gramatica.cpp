#include <bits/stdc++.h>
#include <fstream>
using namespace std;
string cad;
bool detectado = 0;
ofstream fout;

void crop(int &i, int &nivel){
    if(cad[i] == '<'){
        while( i < cad.size() && cad[i] != '/' && cad[i]!='>'){
            ++i;
            fout << cad[i];
        }
        int tipo = 0;
        if(cad[i] == '/'){
            nivel--;
            fout << "/";
            ++i;
            tipo = -1;
        }else if(cad[i] == '>'){
            nivel++;
            tipo = 1;
        }
        if(cad[i] == '>'){
            fout << ">";
            while(cad[i] != '>')++i;
            ++i;
            if(nivel == 0){
                detectado = 0;
                return;
            }
        }

        crop(i, nivel);
    }

    ++i;

    crop(i,nivel);

}

void spanner(int &i, int &nivel){
    if(cad[i] == ' ' || cad[i] == ','){
        ++i;
        spanner(i, nivel);
        return;
    }
    if(i < cad.size()-8 && cad.substr(i, 8) == "data-e2e"){
        while(i > 0 && cad[i] != '<')--i;
        detectado = 1;
        nivel = 0;
        crop(i, nivel);
        return;
    }

    if(cad[i] == '/'){
        ++i;
        while(cad[i] !='>')++i;
        ++i;
        return;
    }

    if(cad[i] == '>'){
        ++i;
        return;
    }
}

void etiqueta(int &i, int &nivel){
    spanner(i, nivel);
}

void gram(int &i, int nivel){

    while(i < cad.size()){
        cout << cad[i];
        if(cad[i] == '<'){
            ++i;
            etiqueta(i, nivel);
        }else{
            ++i;
        }
    }
}
ifstream fin;
int main(){
    fout.open("coincidencias.txt");
    fin.open("v2.html");

    int nivel = 0;
    int cont = 0;
    while(getline(fin,cad)){
        int i = 0;
        ++cont;
        if(cont % 100 == 0)cout << cont << "\n";
        while(i < cad.size()){
            if(!detectado)gram(i, nivel);
            else crop(i, nivel);
        }
    }

}