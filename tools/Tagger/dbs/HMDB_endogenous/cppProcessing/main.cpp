#include<iostream>
#include<fstream>
#include<string>
#include<algorithm>
#include<vector>
#include<iomanip>

using namespace std;

#define TESTING "testing_table.tsv"
#define ENDOGENOUS "endogenous_list.tsv"

/* DECLARE */



/* MAIN */
int main()
{
    // open endogenous array
    vector<string> endogArr = {"aaaa"};

    ifstream myFile(ENDOGENOUS);

    string line;
    while(getline(myFile, line))
    {
        endogArr.push_back(line);
    }

    myFile.close();

    // open testing table
    vector<string> testComp;
    vector<string> testID;

    ifstream myFile2(TESTING);

    while(getline(myFile2, line))
    {
        string token1, token2;
        token1 = line.substr(0, line.find("\t", 0));
        token2 = line.substr(line.find("\t", 0)+1);
        testComp.push_back(token1);
        testID.push_back(token2);
    }

    myFile2.close();

    // Compare each testComp with all endogenous
    vector<string> excludedID;
    float count = 0, percent=0;
    for (int i=0; i<testComp.size(); i++)
    {
        for (int j=0; j<endogArr.size(); j++)
        {
            if (testComp[i] == endogArr[j])
            {
                // cout << testComp[i] << endl;
                excludedID.push_back(testID[i]);
                break;
            }
        }
        count++;
        if (count/testComp.size()*100 >= 0.1)
        {
            percent += 0.1;
            cout << fixed << setprecision(1) << percent << "%" << endl;
            count = 0;
            // break; // test with few examples
        }
    }

    // Get indexes that will be printed in output table
    vector<int> indexes;

    for (int i=0; i<testID.size(); i++)
    {
        if (find(excludedID.begin(), excludedID.end(), testID[i]) == excludedID.end())
        {
            indexes.push_back(i);
            continue;
        }
        // cout << testComp[i] << endl;
    }

    // Print output table
    ofstream myFile3("filtered.tsv");

    myFile3 << "Name" << "\t" << "LOTUS_ID";
    for (int i : indexes)
    {   
        myFile3 << endl;
        myFile3 << testComp[i] << "\t" << testID[i];
    }

    myFile3.close();
    
    return 0;
}


/* DEFINE */