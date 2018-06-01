//////////////////////////////////////////////////////////////////////////
//
// DMM Technology Corp.
//
// File:         DYN232M C++ Sample Program (Form1.h)
//
// Revision:     Version 11.28
//
//
// Notes:		 1.  If getting compile time error "error C2664: 'CreateFileW' : cannot convert parameter 1 from 'const char [5]' to 'LPCWSTR'", 
//					 change project character to "Not Set".  Properties->Configuration Properties/General->Character Set->Not Set
//				 2.  No external dependencies
//
//
//////////////////////////////////////////////////////////////////////////



#pragma once
#include <Windows.h>

namespace DYN232MCSampleCodeV1128 {

// DMM variables
#define General_Read 0x0e
#define		Set_Origin			0x00
#define Go_Absolute_Pos			0x01
#define Make_LinearLine			0x02
#define Go_Relative_Pos			0x03
#define Make_CircluarArc		0x04	//#define Go_Relative_PosM		0x04
#define Assign_Driver_ID        0x05
#define Read_Driver_ID          0x06
#define Set_Driver_Config       0x07
#define Read_Driver_Config      0x08
#define Read_Driver_Status      0x09
#define Turn_ConstSpeed	        0x0a
#define	Square_Wave				0x0b
#define	Sin_Wave				0x0c
#define	SS_Frequency			0x0d
#define Read_PosCmd32			0x0e
#define Set_MainGain            0x10
#define Set_SpeedGain           0x11
#define Set_IntGain             0x12
#define Set_TrqCons             0x13
#define	Set_HighSpeed			0x14
#define	Set_HighAccel			0x15
#define Set_Pos_OnRange         0x16
#define	Set_FoldNumber			0x17
#define Read_MainGain           0x18
#define Read_SpeedGain          0x19
#define Read_IntGain            0x1a
#define Read_TrqCons            0x1b
#define	Read_HighSpeed			0x1c
#define	Read_HighAccel			0x1d
#define Read_Pos_OnRange        0x1e
#define Read_FoldNumber			0x1f
/* functions (sent by driver)       */
#define Is_MainGain             0x10
#define Is_SpeedGain            0x11
#define Is_IntGain              0x12
#define Is_TrqCons              0x13
#define	Is_HighSpeed			0x14
#define	Is_HighAccel			0x15
#define	Is_Driver_ID			0x16
#define Is_Pos_OnRange          0x17
#define	Is_FoldNumber			0x18
#define Is_Status               0x19
#define Is_Config               0x1a
/*For driver status*/
#define	Driver_OnPos			0xfe
#define	Driver_Busy				0x01        /*for b0 */
#define Driver_Servo            0xfd
#define Driver_Free             0x02        /*for b1 */
#define Driver_Normal           0x00
#define Driver_LostPhase        0x04
#define Driver_OverCurrent      0x08
#define Driver_OverHeat         0x0c        /*for b4 b3 b2 */
#define	Driver_OverVolts		0x14
#define Is_AbsPos32				0x1b		// Absolute position 32
#define Is_TrqCurrent			0x1e		// Motor current
//Following are used for Machine Code interpreting
#define	Line_Error			0xff
#define	Line_OK				0x00
#define	Motor_OnPos			0x00
#define	Motor_Busy			0x01
#define	Motor_Free			0x02
#define	Motor_Alarm			0x03

	// DMM Servo Parameters

	char InputBuffer[256];
	char OutputBuffer[256];

	unsigned char packagedReceivedFlag=0x00;

	unsigned char InBfTopPointer,InBfBtmPointer;
	unsigned char OutBfTopPointer,OutBfBtmPointer;

	unsigned char Read_Package_Buffer[8],Read_Num,Read_Package_Length;
	unsigned char Motor_Status[128];

	unsigned char Driver_MainGain;
	unsigned char Driver_SpeedGain;
	unsigned char Driver_IntGain;
	unsigned char Driver_TrqCons;
	unsigned char Driver_HighSpeed;
	unsigned char Driver_HighAccel;
	unsigned char Driver_ReadID;
	unsigned char Driver_OnRange;
			  int Driver_Fold_Number;
			  int Driver_EncoderLine_Number;
	unsigned char Driver_Status;
	unsigned char Driver_Config;
	int Gear_Number[3];					//Read X,Y,Z Gear_Number
	int ParamIntGearNum;
	int ParamIntLineNum;

	long Motor_Pos32;
	long MotorTorqueCurrent,OnPos_read;

	// END - DMM Servo Parameters

	// Serial Variables
	unsigned char Global_Func;

	unsigned char Com_Port;

	HANDLE  hPort;
	HANDLE  hThread;
	COMMTIMEOUTS m_CommTimeouts;
	DCB  dcbCommPort;
	DWORD dwThread;

	BOOL  Comm_Flag;
	// End Serial Parameters

	using namespace System;
	using namespace System::ComponentModel;
	using namespace System::Collections;
	using namespace System::Windows::Forms;
	using namespace System::Data;
	using namespace System::Drawing;

	/// <summary>
	/// Summary for Form1
	/// </summary>
	public ref class Form1 : public System::Windows::Forms::Form
	{
	public:
		Form1(void)
		{
			InitializeComponent();
			//
			//TODO: Add the constructor code here
			//
		}

	protected:
		/// <summary>
		/// Clean up any resources being used.
		/// </summary>
		~Form1()
		{
			if (components)
			{
				delete components;
			}
		}
	private: System::Windows::Forms::Label^  label1;
	protected: 
	private: System::Windows::Forms::TextBox^  textBox1;
	private: System::Windows::Forms::Button^  button1;
	private: System::Windows::Forms::Button^  button2;
	private: System::Windows::Forms::TextBox^  textBox2;
	private: System::Windows::Forms::Label^  label2;
	private: System::Windows::Forms::Label^  label3;
	private: System::Windows::Forms::Label^  label4;
	private: System::Windows::Forms::TextBox^  textBox3;
	private: System::Windows::Forms::Label^  label5;
	private: System::Windows::Forms::TextBox^  textBox4;
	private: System::Windows::Forms::Button^  button3;

	private:
		/// <summary>
		/// Required designer variable.
		/// </summary>
		System::ComponentModel::Container ^components;

#pragma region Windows Form Designer generated code
		/// <summary>
		/// Required method for Designer support - do not modify
		/// the contents of this method with the code editor.
		/// </summary>
		void InitializeComponent(void)
		{
			this->label1 = (gcnew System::Windows::Forms::Label());
			this->textBox1 = (gcnew System::Windows::Forms::TextBox());
			this->button1 = (gcnew System::Windows::Forms::Button());
			this->button2 = (gcnew System::Windows::Forms::Button());
			this->textBox2 = (gcnew System::Windows::Forms::TextBox());
			this->label2 = (gcnew System::Windows::Forms::Label());
			this->label3 = (gcnew System::Windows::Forms::Label());
			this->label4 = (gcnew System::Windows::Forms::Label());
			this->textBox3 = (gcnew System::Windows::Forms::TextBox());
			this->label5 = (gcnew System::Windows::Forms::Label());
			this->textBox4 = (gcnew System::Windows::Forms::TextBox());
			this->button3 = (gcnew System::Windows::Forms::Button());
			this->SuspendLayout();
			// 
			// label1
			// 
			this->label1->AutoSize = true;
			this->label1->Location = System::Drawing::Point(17, 32);
			this->label1->Name = L"label1";
			this->label1->Size = System::Drawing::Size(79, 13);
			this->label1->TabIndex = 0;
			this->label1->Text = L"Set COM Port#";
			// 
			// textBox1
			// 
			this->textBox1->Location = System::Drawing::Point(202, 29);
			this->textBox1->Name = L"textBox1";
			this->textBox1->Size = System::Drawing::Size(65, 20);
			this->textBox1->TabIndex = 1;
			this->textBox1->Text = L"1";
			this->textBox1->TextAlign = System::Windows::Forms::HorizontalAlignment::Right;
			// 
			// button1
			// 
			this->button1->Location = System::Drawing::Point(20, 74);
			this->button1->Name = L"button1";
			this->button1->Size = System::Drawing::Size(109, 23);
			this->button1->TabIndex = 2;
			this->button1->Text = L"Read Encoder";
			this->button1->UseVisualStyleBackColor = true;
			this->button1->Click += gcnew System::EventHandler(this, &Form1::button1_Click);
			// 
			// button2
			// 
			this->button2->Location = System::Drawing::Point(20, 119);
			this->button2->Name = L"button2";
			this->button2->Size = System::Drawing::Size(109, 23);
			this->button2->TabIndex = 3;
			this->button2->Text = L"Move Relative";
			this->button2->UseVisualStyleBackColor = true;
			this->button2->Click += gcnew System::EventHandler(this, &Form1::button2_Click);
			// 
			// textBox2
			// 
			this->textBox2->Location = System::Drawing::Point(167, 76);
			this->textBox2->Name = L"textBox2";
			this->textBox2->ReadOnly = true;
			this->textBox2->Size = System::Drawing::Size(100, 20);
			this->textBox2->TabIndex = 4;
			this->textBox2->TextAlign = System::Windows::Forms::HorizontalAlignment::Right;
			// 
			// label2
			// 
			this->label2->AutoSize = true;
			this->label2->Location = System::Drawing::Point(164, 32);
			this->label2->Name = L"label2";
			this->label2->Size = System::Drawing::Size(32, 13);
			this->label2->TabIndex = 5;
			this->label2->Text = L"1 ~ 8";
			// 
			// label3
			// 
			this->label3->AutoSize = true;
			this->label3->Location = System::Drawing::Point(164, 60);
			this->label3->Name = L"label3";
			this->label3->Size = System::Drawing::Size(87, 13);
			this->label3->TabIndex = 6;
			this->label3->Text = L"Encoder Position";
			// 
			// label4
			// 
			this->label4->AutoSize = true;
			this->label4->Location = System::Drawing::Point(164, 105);
			this->label4->Name = L"label4";
			this->label4->Size = System::Drawing::Size(100, 13);
			this->label4->TabIndex = 8;
			this->label4->Text = L"Relative Move Cmd";
			// 
			// textBox3
			// 
			this->textBox3->Location = System::Drawing::Point(167, 121);
			this->textBox3->Name = L"textBox3";
			this->textBox3->Size = System::Drawing::Size(100, 20);
			this->textBox3->TabIndex = 7;
			this->textBox3->Text = L"0";
			this->textBox3->TextAlign = System::Windows::Forms::HorizontalAlignment::Right;
			// 
			// label5
			// 
			this->label5->AutoSize = true;
			this->label5->Location = System::Drawing::Point(164, 151);
			this->label5->Name = L"label5";
			this->label5->Size = System::Drawing::Size(102, 13);
			this->label5->TabIndex = 11;
			this->label5->Text = L"Absolute Move Cmd";
			// 
			// textBox4
			// 
			this->textBox4->Location = System::Drawing::Point(167, 167);
			this->textBox4->Name = L"textBox4";
			this->textBox4->Size = System::Drawing::Size(100, 20);
			this->textBox4->TabIndex = 10;
			this->textBox4->Text = L"0";
			this->textBox4->TextAlign = System::Windows::Forms::HorizontalAlignment::Right;
			// 
			// button3
			// 
			this->button3->Location = System::Drawing::Point(20, 165);
			this->button3->Name = L"button3";
			this->button3->Size = System::Drawing::Size(109, 23);
			this->button3->TabIndex = 9;
			this->button3->Text = L"Move Absolute";
			this->button3->UseVisualStyleBackColor = true;
			this->button3->Click += gcnew System::EventHandler(this, &Form1::button3_Click_1);
			// 
			// Form1
			// 
			this->AutoScaleDimensions = System::Drawing::SizeF(6, 13);
			this->AutoScaleMode = System::Windows::Forms::AutoScaleMode::Font;
			this->ClientSize = System::Drawing::Size(284, 205);
			this->Controls->Add(this->label5);
			this->Controls->Add(this->textBox4);
			this->Controls->Add(this->button3);
			this->Controls->Add(this->label4);
			this->Controls->Add(this->textBox3);
			this->Controls->Add(this->label3);
			this->Controls->Add(this->label2);
			this->Controls->Add(this->textBox2);
			this->Controls->Add(this->button2);
			this->Controls->Add(this->button1);
			this->Controls->Add(this->textBox1);
			this->Controls->Add(this->label1);
			this->Name = L"Form1";
			this->Text = L"Form1";
			this->ResumeLayout(false);
			this->PerformLayout();

		}
#pragma endregion

		///////////////////////////     START VISUAL STUDIO SERIAL FUNCTIONS		///////////////////////////////////


void serialinit()		//this main serialinit() should only be called if the user has already set the COM Port
{
	char global_UserComPort=Int32::Parse(textBox1->Text);
	switch(global_UserComPort)
	{
		case  1: hPort =	CreateFile("COM1",GENERIC_READ|GENERIC_WRITE,0,NULL,OPEN_EXISTING,0,NULL); break;
		case  2: hPort =	CreateFile("COM2",GENERIC_READ|GENERIC_WRITE,0,NULL,OPEN_EXISTING,0,NULL); break;
		case  3: hPort =	CreateFile("COM3",GENERIC_READ|GENERIC_WRITE,0,NULL,OPEN_EXISTING,0,NULL); break;
		case  4: hPort =	CreateFile("COM4",GENERIC_READ|GENERIC_WRITE,0,NULL,OPEN_EXISTING,0,NULL); break;
		case  5: hPort =	CreateFile("COM5",GENERIC_READ|GENERIC_WRITE,0,NULL,OPEN_EXISTING,0,NULL); break;
		case  6: hPort =	CreateFile("COM6",GENERIC_READ|GENERIC_WRITE,0,NULL,OPEN_EXISTING,0,NULL); break;
		case  7: hPort =	CreateFile("COM7",GENERIC_READ|GENERIC_WRITE,0,NULL,OPEN_EXISTING,0,NULL); break;
		case  8: hPort =	CreateFile("COM8",GENERIC_READ|GENERIC_WRITE,0,NULL,OPEN_EXISTING,0,NULL); break;
		default: hPort =	CreateFile("COM1",GENERIC_READ|GENERIC_WRITE,0,NULL,OPEN_EXISTING,0,NULL);
	}

	if(hPort==INVALID_HANDLE_VALUE)
	{
		if(GetLastError()==ERROR_FILE_NOT_FOUND)
		{
			//cout<<"Error: serial port does not exist."<<"\n";  //serial port does not exist. Inform user.
		}
		//cout<<"Some other error occurred. Inform user."<<"\n";
	}

	BOOL Comm_Flag;
	Comm_Flag = SetupComm(hPort, 256, 256);		// set buffer sizes, SetupComm(Handle,in,out)

	DCB dcb;
	dcb.DCBlength = sizeof (DCB);
	//cout<<"Variable dbc length = "<<sizeof (DCB)<<"\n";
	
	if (!GetCommState(hPort, &dcb)) 
	{
		//cout<<"*Error Getting State"<<"\n";
	}

	dcb.BaudRate = CBR_38400; //Baud
	dcb.ByteSize = 8; //8 data bits
	dcb.Parity = NOPARITY; //no parity
	dcb.StopBits = ONESTOPBIT; //1 stop

	if(!SetCommState(hPort, &dcb))
	{
		//cout<<"*Error Setting Serial Port State"<<"\n";
	}

	COMMTIMEOUTS timeouts;
	timeouts.ReadIntervalTimeout=5;
	timeouts.ReadTotalTimeoutConstant=1;
	timeouts.ReadTotalTimeoutMultiplier=1;
	timeouts.WriteTotalTimeoutConstant=100;
	timeouts.WriteTotalTimeoutMultiplier=1;
	if(!SetCommTimeouts(hPort, &timeouts))
	{
		//cout<<"*Timeout Set Error Occured"<<"\n";//error occureed. Inform user
	}
	//cout<<"Timeouts Set!"<<"\n";
}

void closeserial()
{
	CloseHandle(hPort);
	//cout<<"Serial Port Closed."<<"\n";
}

///////////////////////////     END VISUAL STUDIO SERIAL FUNCTIONS		///////////////////////////////////



///////////////////////////     START DMM SERVO FUNCTIONS		///////////////////////////////////

void ReadPackage()
{
	unsigned char c,cif;
	
	BOOL Read_Flag;
	DWORD dwBytesRead = 0;

    Read_Flag = ReadFile(hPort,&c,1,&dwBytesRead,NULL);
	while(dwBytesRead==1)
	{
		InputBuffer[InBfTopPointer] = c;
		InBfTopPointer++;
		Read_Flag = ReadFile(hPort,&c,1,&dwBytesRead,NULL);
	}
	
	while(InBfBtmPointer!=InBfTopPointer)
	{
		c = InputBuffer[InBfBtmPointer];
		InBfBtmPointer++;
		cif = c&0x80;
		
		if(cif==0)
		{
			Read_Num = 0;
			Read_Package_Length = 0;
		}
	
		if(cif==0||Read_Num>0)
		{
			Read_Package_Buffer[Read_Num] = c;
			Read_Num++;
			if(Read_Num==2)
			{
				cif = c>>5;
				cif = cif&0x03;
				Read_Package_Length = 4 + cif;
				c = 0;
			}
	
			if(Read_Num==Read_Package_Length)
			{
				Get_Function();
				Read_Num = 0;
				Read_Package_Length = 0;
			}
		}
	}
}

char ReadByte()
{
	char c;
		c = InputBuffer[InBfBtmPointer];
	return(c);
}

void Get_Function(void)
{
	char ID,Function_Code,CRC_Check;
	long TempPos32,Temp32;

	ID = Read_Package_Buffer[0]&0x7f;
	Function_Code = Read_Package_Buffer[1]&0x1f;
	
	CRC_Check = 0;
	for(int i=0;i<Read_Package_Length-1;i++)
	 CRC_Check += Read_Package_Buffer[i];
	 CRC_Check ^= Read_Package_Buffer[Read_Package_Length-1];
	 CRC_Check &= 0x7f;
	if(CRC_Check!= 0)
	{
		//MessageBox::Show(L"There is CRC Error",L"CRC Error",MessageBoxButtons::OK,MessageBoxIcon::Error);
	}
	else
	{
		switch(Function_Code)
		{
			case  Is_MainGain:
				Driver_MainGain = (char)Cal_SignValue(Read_Package_Buffer);
				Driver_MainGain = Driver_MainGain & 0x7f;
				break;
			case  Is_SpeedGain:
				Driver_SpeedGain = (char)Cal_SignValue(Read_Package_Buffer);
				Driver_SpeedGain = Driver_SpeedGain & 0x7f;
				break;
			case  Is_IntGain:
				Driver_IntGain = (char)Cal_SignValue(Read_Package_Buffer);
				Driver_IntGain = Driver_IntGain & 0x7f;
				break;
			case  Is_TrqCons:
				Driver_TrqCons = (char)Cal_SignValue(Read_Package_Buffer);
				Driver_TrqCons = Driver_TrqCons & 0x7f;
				break;
			case  Is_HighSpeed:
				Driver_HighSpeed = (char)Cal_SignValue(Read_Package_Buffer);
				Driver_HighSpeed = Driver_HighSpeed & 0x7f;
				break;
			case  Is_HighAccel:
				Driver_HighAccel = (char)Cal_SignValue(Read_Package_Buffer);
				Driver_HighAccel = Driver_HighAccel & 0x7f;
				break;
			case  Is_Driver_ID:
				Driver_ReadID = ID;
				break;
			case  Is_Pos_OnRange:
				Driver_OnRange = (char)Cal_SignValue(Read_Package_Buffer);
				Driver_OnRange = Driver_OnRange & 0x7f;
				break;

			case  Is_FoldNumber:                                   
				Temp32 = Cal_Value(Read_Package_Buffer);
				Driver_Fold_Number = Temp32 & 0x0000ffff;
				if( ID < 3)
					Gear_Number[ID] = Driver_Fold_Number;
				Temp32 = Temp32 >> 16;
				Driver_EncoderLine_Number = Temp32;
				break;
		
			case  Is_Status:
				Driver_Status = (char)Cal_SignValue(Read_Package_Buffer);
					if((Driver_Status&0x01)==0)
						Motor_Status[ID] = 	Motor_OnPos;
					else
						Motor_Status[ID] = 	Motor_OnPos;			//Motor_Busy;
		
					if((Driver_Status&0x1c)!=0)
						Motor_Status[ID] = 	Motor_Alarm;
		
					if((Driver_Status&0x02)!=0)
						Motor_Status[ID] = 	Motor_Free;	
				break;

			case  Is_Config:
				Driver_Config = (char)Cal_SignValue(Read_Package_Buffer);
				break;
			case  Is_AbsPos32:
				packagedReceivedFlag=0xff;
				Motor_Pos32 = Cal_SignValue(Read_Package_Buffer);	
				break;
			case  Is_TrqCurrent:
				packagedReceivedFlag=0xff;
				MotorTorqueCurrent = Cal_SignValue(Read_Package_Buffer);
				break;
			default:;
		}
	}
}


/*Get data with sign - long*/
//array<unsigned char>^ One_Package=gcnew array<unsigned char>(8)
//long Cal_SignValue(unsigned char One_Package[8])
long Cal_SignValue(unsigned char One_Package[8])
{
	char Package_Length,OneChar,i;
	long Lcmd;
	OneChar = One_Package[1];
	OneChar = OneChar>>5;
	OneChar = OneChar&0x03;
	Package_Length = 4 + OneChar;
	OneChar = One_Package[2];			/*First byte 0x7f, bit 6 reprents sign */
	OneChar = OneChar << 1;
	Lcmd = (long)OneChar;			/* Sign extended to 32bits */
	Lcmd = Lcmd >> 1;
	for(i=3;i<Package_Length-1;i++)
	{
		OneChar = One_Package[i];
		OneChar &= 0x7f;
		Lcmd = Lcmd<<7;
		Lcmd += OneChar;
	}
	return(Lcmd);				/* Lcmd : -2^27 ~ 2^27 - 1 */
}

long Cal_Value(unsigned char One_Package[8])
{
	char Package_Length,OneChar,i;
	long Lcmd;
	OneChar = One_Package[1];
	OneChar = OneChar>>5;
	OneChar = OneChar&0x03;
	Package_Length = 4 + OneChar;

	OneChar = One_Package[2];		/*First byte 0x7f, bit 6 reprents sign			*/
	OneChar &= 0x7f;
	Lcmd = (long)OneChar;			/*Sign extended to 32bits						*/
	for(i=3;i<Package_Length-1;i++)
	{
		OneChar = One_Package[i];
		OneChar &= 0x7f;
		Lcmd = Lcmd<<7;
		Lcmd += OneChar;
	}
	return(Lcmd);					/*Lcmd : -2^27 ~ 2^27 - 1						*/
}

//***************** Every Robot Instruction ******************
// Send a package with a function by Global_Func
// Displacement: -2^27 ~ 2^27 - 1


void Send_Package(char ID , long Displacement)
{
	unsigned char B[8],Package_Length,Function_Code;
	long TempLong;
	B[1] = B[2] = B[3] = B[4] = B[5] = (unsigned char)0x80;
	B[0] = ID&0x7f;
	Function_Code = Global_Func & 0x1f;
	
	TempLong = Displacement & 0x0fffffff;		//Max 28bits
	B[5] += (unsigned char)TempLong&0x0000007f;
	TempLong = TempLong>>7;
	B[4] += (unsigned char)TempLong&0x0000007f;
	TempLong = TempLong>>7;
	B[3] += (unsigned char)TempLong&0x0000007f;
	TempLong = TempLong>>7;
	B[2] += (unsigned char)TempLong&0x0000007f;	
	Package_Length = 7;

	TempLong = Displacement;
	TempLong = TempLong >> 20;
	if(( TempLong == 0x00000000) || ( TempLong == 0xffffffff))
	{//Three byte data
		B[2] = B[3];
		B[3] = B[4];
		B[4] = B[5];
		Package_Length = 6;
	}
	
	TempLong = Displacement;
	TempLong = TempLong >> 13;
	if(( TempLong == 0x00000000) || ( TempLong == 0xffffffff))
	{//Two byte data
		B[2] = B[3];
		B[3] = B[4];
		Package_Length = 5;
	}
	
	TempLong = Displacement;
	TempLong = TempLong >> 6;
	if(( TempLong == 0x00000000) || ( TempLong == 0xffffffff))
	{//One byte data
		B[2] = B[3];
		Package_Length = 4;
	}

	B[1] += (Package_Length-4)*32 + Function_Code; 
	
	//long x = Cal_SignValue(B);
	Make_CRC_Send(Package_Length,B);
}

void Make_CRC_Send(unsigned char Plength,unsigned char B[8])
{
	unsigned char Error_Check = 0;
	for(int i=0;i<Plength-1;i++)
	{
		OutputBuffer[OutBfTopPointer] = B[i];
		OutBfTopPointer++;
		Error_Check += B[i];
	}
	Error_Check = Error_Check|0x80;
	OutputBuffer[OutBfTopPointer] = Error_Check;
	OutBfTopPointer++;
	
	WritePackage();
}

void WritePackage()
{
	unsigned char i;
	char c;
	while(OutBfBtmPointer!=OutBfTopPointer)
	{
		c = OutputBuffer[OutBfBtmPointer];
		WriteByte(c);
		OutBfBtmPointer++;
		i = 10;
		while(i!=0)
		  i--;
	}	
}

void WriteByte(char c)
{
	DWORD  dwCount;

		Comm_Flag = WriteFile(hPort,&c,1,&dwCount,NULL);
		if(!Comm_Flag)
		{
			//MessageBox("Error in writing RS232");
			exit(0);
		}
		int j = 0;
	for(int i=0;i<=200;i++)
		j++;
	ReadCommPort();
}

void ReadCommPort()
{
	DWORD dwBytesRead = 0;
	char c;
	BOOL Read_Flag;

    Read_Flag = ReadFile(hPort,&c,1,&dwBytesRead,NULL);
	while(dwBytesRead==1)
	{
		InputBuffer[InBfTopPointer] = c;
		InBfTopPointer++;
		Read_Flag = ReadFile(hPort,&c,1,&dwBytesRead,NULL);
	}
}


///////////////////////////     END DMM SERVO FUNCTIONS		///////////////////////////////////


	// READ ENCODER POSITION
	private: System::Void button1_Click(System::Object^  sender, System::EventArgs^  e) 
			 {
				 char Axis_Num = 0;		// Assume connect drive ID = 0;
				 serialinit();
				 Global_Func = (char)General_Read;
				 Send_Package(Axis_Num, Is_AbsPos32);
				 Sleep(100);
				 ReadPackage();
				 closeserial();
				 textBox2->Text=Convert::ToString(Motor_Pos32);
			 }

	// MOVE RELATIVE POSITION
	private: System::Void button2_Click(System::Object^  sender, System::EventArgs^  e) 
			 {
					 char Axis_Num = 0;		// Assume connect drive ID = 0;
					 serialinit();
					 Global_Func = (char)Go_Relative_Pos;
					 long pos=Int32::Parse(textBox3->Text);
					 Send_Package(Axis_Num,pos);
					 closeserial();
			 }

	// MOVE ABSOLUTE POSITION
	private: System::Void button3_Click_1(System::Object^  sender, System::EventArgs^  e) 
			{
					 char Axis_Num = 0;		// Assume connect drive ID = 0;
					 serialinit();
					 Global_Func = (char)Go_Absolute_Pos;
					 long pos=Int32::Parse(textBox4->Text);
					 Send_Package(Axis_Num,pos);
					 closeserial();
			}


};
}
