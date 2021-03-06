package com.ford.evsmartcharge;

import android.bluetooth.BluetoothHeadset;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.StrictMode;
import android.support.annotation.Nullable;
import android.support.v4.app.Fragment;
import android.support.v7.preference.PreferenceManager;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.SeekBar;
import android.widget.TextView;
import android.widget.TimePicker;

import java.util.Calendar;



import com.google.firebase.database.DatabaseReference;

import com.rabbitmq.client.*;

import java.text.DecimalFormat;
import java.util.Date;

public class HomeMenu extends Fragment implements View.OnClickListener {





    private SeekBar mSeekBar;
    private TextView mChargeText;
    private TextView mFeedbackText;
    private TimePicker mTimePicker;
    private Button mButton;
    private RadioGroup mRadioGroup;
    private RadioButton mRadioButton;
    private Intent login, login2;
    private SharedPreferences mPref;
    private String message = "";
    private Intent i;
    private char bvalue[] = new char[1024];
    private SharedPreferences.Editor mPrefEdit;
    private BluetoothHeadset mBluetoothHeadset;
    private double batteryCapacity = 0;
    private DatabaseReference mDatabase;
    private static final String TAG = HomeMenu.class.getSimpleName();
    private String portNumber = "0";
    private String rCharge = "";
    private Date currentTime = Calendar.getInstance().getTime();


    //String to store app information to send to simulation
    /*
    All encoded parsing helpers
    Battery Capacity    "-BC:"
    Charge Speed        "-CS:"
    Charge Update `     "-CU:"
    Charge Request      "-CR:"
    Port Request        "-PR:"
     */




    @Nullable
    @Override
    public View onCreateView(LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        //returning our layout file
        mPref = PreferenceManager.getDefaultSharedPreferences(getActivity());
        mPrefEdit = mPref.edit();
        return inflater.inflate(R.layout.fragment_home_menu, container, false);
    }



    @Override
    public void onViewCreated(View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        getActivity().setTitle("Home");
        System.out.println("initial charge is " + MainActivity.initialCharge);

        mSeekBar = (SeekBar) getActivity().findViewById(R.id.charge_bar);
        //mSeekBar.setProgress(mPref.getInt(getString(R.string.slider_location), 69));
        if(mPref.getInt(getString(R.string.slider_location), 0) == -1) {
            System.out.println("STORED VAL IS -1");
            mSeekBar.setProgress(MainActivity.initialCharge);
        } else {
            mSeekBar.setProgress(mPref.getInt(getString(R.string.slider_location), 0));

        }

        mChargeText = (TextView) getActivity().findViewById(R.id.charge_text);
        mFeedbackText = (TextView) getActivity().findViewById(R.id.feedback_text);
        mTimePicker = (TimePicker) getActivity().findViewById(R.id.time_picker);
        mButton = (Button) getActivity().findViewById(R.id.button);
        mRadioGroup = (RadioGroup) getActivity().findViewById(R.id.portpicker);
        mRadioButton = (RadioButton) getActivity().findViewById(R.id.buttZero);
        mRadioButton.setChecked(true);


        switch(mPref.getString(this.getString(R.string.pref_car_key), "0")) {
            case "0": // C-Max Energi SE
                batteryCapacity = 8.0;
                mSeekBar.setMax(100);                   // Sets seekbar to 100%
             message += "-BC:" + batteryCapacity; // Sets battery cap to comm. string
                break;
            case "1": // Fusion Energi SE
                batteryCapacity = 9.0;
                mSeekBar.setMax(100);       // Sets seekbar to 100%
                message += "-BC:" + batteryCapacity; // Sets battery cap to comm. string
                break;
            case "2": // Focus Electric
                batteryCapacity = 33.5;
                mSeekBar.setMax(100);       // Sets seekbar to 100%
                message += "-BC:" + batteryCapacity; // Sets battery cap to comm. string
                break;
            default:
                Log.d(TAG, "Invalid value");
        }

        updateChargeText();

        // Seek bar listener
        mSeekBar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int i, boolean b) {
                if(isAboveInitialSOC()) {
                    updateChargeText();
                    mFeedbackText.setText(new StringBuilder(""));
                }
                else {
                    mSeekBar.setProgress(MainActivity.initialCharge);
                    mFeedbackText.setText(new StringBuilder("You cannot request a charge value " +
                            "below your battery's current state of charge"));
                }
                mPrefEdit.putInt(getString(R.string.slider_location), mSeekBar.getProgress());
                mPrefEdit.commit();
            }
            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {}
            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {}
        });

        // Button listener
        mButton.setOnClickListener(this);
    }

    @Override
    public void onDestroyView() {
        super.onDestroyView();

        mPrefEdit.putInt(getString(R.string.slider_location), mSeekBar.getProgress());
        mPrefEdit.commit();

    }

    @Override
    public void onClick(View view) {
        switch (view.getId()) {
            case R.id.button:
                submitChargeRequest(view);
                break;
            default:
                break;
        }
    }

    private boolean isAboveInitialSOC() {
        if(mSeekBar.getProgress() >= MainActivity.initialCharge)
            return true;
        else
            return false;
    }

    // updates the displayed charge percent/miles below the seek bar
    public void updateChargeText()
    {
        int seekVal = mSeekBar.getProgress();
        String x = "";

        if(mPref.getString(this.getString(R.string.pref_unit_key), "0").equals("1")) {
            // Miles - assuming 4 mi/kWh
            int miles = (4 * (int) ((batteryCapacity) * (seekVal / 100.)));
            //Removed decimal to look pretty
            //DecimalFormat df = new DecimalFormat("#.##");
            x += /*df.format(miles)*/ miles + " miles";
        } else if(mPref.getString(this.getString(R.string.pref_unit_key), "0").equals("2")) {
            // Kilometers calculated from Miles - assuming 4 mi/kWh
            int kilometers = (4 * (int)((batteryCapacity) * 1.60934 * (seekVal/100.)));
            //Removed decimal to look pretty
            //DecimalFormat df = new DecimalFormat("#.##");
            x += /*df.format(kilometers)*/ kilometers + " kilometers";
        } else {
            // SOC %
            x += seekVal + "% Charge";
        }

        mChargeText.setText(new StringBuilder(x));
    }


    // Take the desired time & requested charge amount
    // Print these values, forward to station simulation
    // ** Simulation will change start time, but keep desired end time **
    public void submitChargeRequest(View view) {
        int hour = mTimePicker.getCurrentHour();
        int min = mTimePicker.getCurrentMinute();
        int seekVal = mSeekBar.getProgress();
        int space = mRadioGroup.getCheckedRadioButtonId();
        int port_num = 0;


        switch (space) {
            case R.id.buttZero:
                port_num = 0;
                portNumber = "0";
                break;
            case R.id.buttOne:
                port_num = 1;
                portNumber = "1";
                break;
            case R.id.buttTwo:
                port_num = 2;
                portNumber = "2";
                break;
            case R.id.buttThree:
                port_num = 3;
                portNumber = "3";
                break;

        }

        // send packet to station
        new PostTask().execute(Double.toString(batteryCapacity), Integer.toString(MainActivity.initialCharge),
                Integer.toString(hour), Integer.toString(min), Integer.toString(seekVal), Integer.toString(port_num));

        // format the time for better readability
        String format;
        String zero = "";
        if (hour == 0) {
            hour += 12;
            format = "AM";
        } else if (hour == 12) {
            format = "PM";
        } else if (hour > 12) {
            hour -= 12;
            format = "PM";
        } else {
            format = "AM";
        }
        if (min < 10) {
            zero = "0";
        }

        // Format charge as percentage, miles, or kilometers
        String requestedCharge = "";
        rCharge = String.valueOf(seekVal);
        if (mPref.getString(this.getString(R.string.pref_unit_key), "0").equals("1")) { // miles format

            double miles = (4 * (int) (batteryCapacity) * (seekVal / 100.)); // 4 is arbitrary 4 mi/kWh
            double kilometers = miles * 1.60934;                               // Distance in Kilometers.
            DecimalFormat df = new DecimalFormat("#.##");
            requestedCharge += df.format(miles) + " miles";
            //rCharge += df.format(miles);

        } else if (mPref.getString(this.getString(R.string.pref_unit_key), "0").equals("2")) { // kilometers format

            int kilometers = (4 * (int) ((batteryCapacity) * 1.60934 * (seekVal / 100.)));  // Distance in km. 1.6.934 is conversion factor
            requestedCharge += kilometers + " kilometers";

        } else { // percent format
            requestedCharge += seekVal + "%";
        }
                                    //TODO
        try {
            new Thread(new Runnable(){
                @Override
                public void run() {
                    String EXCHANGE_NAME = "hello";
                    ConnectionFactory factory = new ConnectionFactory();
                    String uri = "amqp://msprqdua:XO-wSDRahPG_y2HHwzLlP80B0NiB31h-@wombat.rmq.cloudamqp.com/msprqdua";   //The URL for AMQP
                    try {
                        factory.setUri(uri);
                        Connection connection = factory.newConnection();
                        Channel channel = connection.createChannel();
                        channel.confirmSelect();
                        factory.setAutomaticRecoveryEnabled(false);

                        //Initiate Message
                        message = "";
                        message += "-BC;" + batteryCapacity;
                        message += "-RC;" + rCharge;
                        message += "-PC;" + seekVal;
                        message += "-PN;" + portNumber;
                        message += "-ET;" + (mTimePicker.getCurrentHour() + Math.round((mTimePicker.getCurrentMinute()/60.0)*100.0)/100.0);

                        channel.basicPublish("", EXCHANGE_NAME, null, message.getBytes());
                        System.out.println(" [x] Sent '" + "ev-sc" + "':'" + message + "'");
                        message = "";
                    } catch(Exception e){
                        System.out.println(e);
                    }
                }
            }).start();

        } catch (Exception e){
            System.out.println(e);
        }


        mFeedbackText.setText(new StringBuilder().append("Your car will be charged to ")
                .append(requestedCharge).append(" by ").append(hour).append(":")
                .append(zero).append(min).append(" ").append(format));


    }



    // The task class
    private class PostTask extends AsyncTask<String, Integer, String> {
        @Override
        protected void onPreExecute() {
            super.onPreExecute();
        }

        @Override
        protected String doInBackground(String... params) {
            String batCap = params[0];
            String initialSOC = params[1];
            String hour = params[2];
            String min = params[3];
            String reqCharge = params[4];
            String port = params[5];
            String userID;
            //Bundle a =login2.getExtras();
            //Bundle b = new Bundle();
            //avalue = (String) a.get("member");

            try {
                /*
                // Get device registration ID
                userID = FirebaseInstanceId.getInstance().getToken();

                // Create message string
                // TODO add userID
                message = userID + " " + port + " " + batCap + " " + initialSOC + " " + hour + " " + min + " " + reqCharge;

                // -- SAVE DATA TO FIREBASE -- //
                mDatabase = FirebaseDatabase.getInstance().getReference();
                mDatabase.child("add").child(userID).setValue(message);



                Socket soc = new Socket("192.168.1.13" , 8888);
                PrintWriter out = new PrintWriter(soc.getOutputStream(), true);
                BufferedReader in = new BufferedReader(
                                        //new InputStreamReader(soc.getInputStream()));
                BufferedReader stdIn =
                        new BufferedReader(new InputStreamReader(System.in));

                out.print(batCap + " " + initialSOC + " " + hour + " " + min + " " + reqCharge);
                out.flush();
                in.read(bvalue,1024,1024);
                i = new Intent(HomeMenu.this.getActivity(), Notification.class);
                i.putExtra("message", bvalue);
                startActivityForResult(i,0);
                soc.close();
                */
                return "1";

            } catch(Exception e){
                e.printStackTrace();
                return "0";
            }
        }

        @Override
        protected void onProgressUpdate(Integer... values) {
            super.onProgressUpdate(values);
        }

        @Override
        protected void onPostExecute(String result) {
            super.onPostExecute(result);
        }


    }
}
