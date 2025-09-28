package client;

import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;
import java.util.Random;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class App {

    public static int devices;
    public static double lamMean;
    public static double lamStd;

    private static final List<DeviceTask> tasks = new ArrayList<>();
    private static ExecutorService executor;

    private static void load() {
        Properties prop = new Properties();
        try (InputStream input = App.class.getClassLoader().getResourceAsStream("application.properties")) {
            prop.load(input);
            System.out.println(prop.getProperty("devices", "100"));
            devices = Integer.parseInt(prop.getProperty("devices", "100"));
            lamMean = Double.parseDouble(prop.getProperty("lam.mean", "1.0"));
            lamStd = Double.parseDouble(prop.getProperty("lam.std", "0.5"));
        } catch (Exception e) {
            throw new RuntimeException("Cannot Read Properties", e);
        }
    }

    public static void main(String[] args) {
        load();

        executor = Executors.newFixedThreadPool(devices);
        
        ShutdownHook shutdownHook = new ShutdownHook();
        Runtime.getRuntime().addShutdownHook(new Thread(shutdownHook, "shutdown Device"));

        initDeviceTasks();
        startDevices();
    }

    private static void initDeviceTasks() {
        Random random = new Random();
        for(int i=1; i<=devices; i++) {
            Device device = new Device(i, lamMean, lamStd, random);
            DeviceTask task = new DeviceTask(device);
            tasks.add(task);
        }
    }

    private static void startDevices() {
        for(DeviceTask task : tasks) {
            task.onDevice(); // 디바이스 실행
            executor.submit(task);
        }
    }

    public static class ShutdownHook implements Runnable {
        @Override
        public void run() {
            System.out.println("Shutdown detected! Stopping all devices...");

            // 모든 디바이스 끄기
            for (DeviceTask task : tasks) {
                task.shutdownDevice();
            }

            // 스레드풀 인터럽트
            executor.shutdownNow();

        }
    }
}
